"""El grafo de la fábrica: un supervisor que enruta entre cuatro agentes especializados.

Flujo: filtro → spec/plan → aprobación humana → código → pruebas → revisión → entrega.
Cada agente vuelve al supervisor, y el supervisor decide con `add_conditional_edges` quién sigue,
según el estado. Todos los ciclos tienen tope y el estado se guarda en cada paso (checkpoints).
"""
import os
from pathlib import Path

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from fabrica.agentes import Agentes
from fabrica.estado import Estado
from fabrica.seguridad import filtrar_entrada, registrar

MAX_CICLOS = 3      # veces que puede escribir código el implementador
MAX_RECHAZOS = 2    # planes rechazados o inválidos antes de escalar a una persona
SALIDA = Path(os.environ.get("FABRICA_SALIDA", "salida"))


def filtro(estado: Estado) -> dict:
    """Seguridad en la entrada: el requisito no es confiable hasta que pasa el filtro."""
    motivo = filtrar_entrada(estado["requisito"])
    registrar("filtro", sospechoso=bool(motivo), motivo=motivo)
    return {"fase": "filtro", "bloqueado": motivo or ""}


def aprobar(estado: Estado) -> dict:
    """Humano en el lazo: el grafo se detiene hasta que una persona aprueba o comenta el plan."""
    respuesta = interrupt({"plan": estado["plan"], "pregunta": "¿Apruebas el plan? Escribe «si» o un comentario."})
    aprobado = str(respuesta).strip().lower() in {"si", "sí", "s"}
    registrar("aprobacion", aprobado=aprobado, comentario="" if aprobado else str(respuesta))
    if aprobado:
        return {"fase": "aprobacion", "aprobado": True, "comentario": ""}
    return {"fase": "aprobacion", "aprobado": False, "plan": {}, "comentario": str(respuesta),
            "rechazos": estado.get("rechazos", 0) + 1}


def supervisor(estado: Estado) -> dict:
    """Coordina, enruta y decide qué agente actúa. No ejecuta ninguna tarea él mismo."""
    fase, errores = estado.get("fase"), estado.get("errores", [])
    ciclos_ok = estado.get("ciclos", 0) < MAX_CICLOS
    rechazos_ok = estado.get("rechazos", 0) <= MAX_RECHAZOS

    if fase == "filtro":
        siguiente = "entregar" if estado.get("bloqueado") else "planificador"
    elif fase == "plan":
        siguiente = "aprobar" if estado.get("plan") else ("planificador" if rechazos_ok else "escalar")
    elif fase == "aprobacion":
        siguiente = "implementador" if estado.get("aprobado") else ("planificador" if rechazos_ok else "escalar")
    elif fase == "codigo":
        siguiente = "tester" if not errores else ("implementador" if ciclos_ok else "escalar")
    elif fase in ("pruebas", "revision"):
        terminado = not errores
        destino = "revisor" if fase == "pruebas" else "entregar"
        siguiente = destino if terminado else ("implementador" if ciclos_ok else "escalar")
    else:
        siguiente = "escalar"

    if siguiente == "escalar":
        return {"siguiente": "entregar", "final": "ESCALAR"}
    if siguiente == "entregar" and not estado.get("final"):
        return {"siguiente": "entregar", "final": "BLOQUEADA" if estado.get("bloqueado") else "LISTA"}
    return {"siguiente": siguiente}


def entregar(estado: Estado) -> dict:
    """Escribe el código, las pruebas y el reporte en salida/<funcion>/ (código + tests + documentación)."""
    nombre = estado.get("plan", {}).get("funcion") or "sin_plan"
    carpeta = SALIDA / nombre
    carpeta.mkdir(parents=True, exist_ok=True)
    if estado.get("codigo") and estado["final"] == "LISTA":
        (carpeta / "modulo.py").write_text(estado["codigo"], encoding="utf-8")
        (carpeta / "test_modulo.py").write_text(estado["pruebas"], encoding="utf-8")
    hallazgos = estado.get("revision", {}).get("hallazgos", [])
    reporte = [f"# Reporte · {nombre}", "", f"**Estado final:** {estado['final']}", "",
               "## Requisito", "", estado["requisito"].strip(), ""]
    if estado.get("bloqueado"):
        reporte += ["## Motivo del bloqueo", "", estado["bloqueado"], ""]
    if estado.get("plan"):
        reporte += ["## Plan", "", f"`{estado['plan']['firma']}`", ""] + [f"1. {t}" for t in estado["plan"]["tareas"]] + [""]
    reporte += ["## Ciclos de corrección", "", f"{estado.get('ciclos', 0)} de {MAX_CICLOS}", ""]
    if estado.get("resultado"):
        reporte += ["## Pruebas", "", "```", estado["resultado"]["salida"].strip()[-1500:], "```", ""]
    if hallazgos:
        reporte += ["## Hallazgos del revisor", ""] + [f"- **{h['severidad']}**: {h['descripcion']}" for h in hallazgos] + [""]
    if estado.get("errores") and estado["final"] == "ESCALAR":
        reporte += ["## Pendiente para una persona", ""] + [f"- {e[:500]}" for e in estado["errores"]] + [""]
    (carpeta / "REPORTE.md").write_text("\n".join(reporte), encoding="utf-8")
    return {}


def construir_grafo(modelo, checkpointer):
    """Arma el StateGraph con el modelo dado (real o falso) y el checkpointer para persistir y pausar."""
    agentes = Agentes(modelo)
    g = StateGraph(Estado)
    g.add_node("filtro", filtro)
    g.add_node("supervisor", supervisor)
    g.add_node("planificador", agentes.planificador)
    g.add_node("aprobar", aprobar)
    g.add_node("implementador", agentes.implementador)
    g.add_node("tester", agentes.tester)
    g.add_node("revisor", agentes.revisor)
    g.add_node("entregar", entregar)

    g.add_edge(START, "filtro")
    for nodo in ("filtro", "planificador", "aprobar", "implementador", "tester", "revisor"):
        g.add_edge(nodo, "supervisor")                      # todos reportan al supervisor
    g.add_conditional_edges("supervisor", lambda e: e["siguiente"],
                            ["planificador", "aprobar", "implementador", "tester", "revisor", "entregar"])
    g.add_edge("entregar", END)
    return g.compile(checkpointer=checkpointer)