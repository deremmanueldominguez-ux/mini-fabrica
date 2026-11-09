"""Los cuatro agentes especializados. Cada uno es un nodo del grafo: `prompt | modelo | parser`.

Un agente nunca decide si su entrega sirve: la valida el código (contratos Pydantic y `seguridad.py`).
Si no sirve, deja los problemas en `errores` y el supervisor decide qué sigue.
"""
import json
import re

from langchain_core.output_parsers import StrOutputParser
from pydantic import ValidationError

from fabrica.estado import Estado, Plan, Revision
from fabrica.prompts import IMPLEMENTADOR, PLANIFICADOR, REVISOR, TESTER
from fabrica.seguridad import ejecutar_en_sandbox, registrar, validar_codigo


def extraer_json(texto: str) -> dict:
    """El primer objeto JSON de la respuesta, aunque venga dentro de un bloque ```json."""
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio < 0 or fin < inicio:
        raise ValueError("la respuesta no trae un objeto JSON")
    return json.loads(texto[inicio:fin + 1])


def extraer_python(texto: str) -> str:
    """El contenido del primer bloque ```python, o el texto completo si no hay bloque."""
    m = re.search(r"```(?:python)?\n(.*?)```", texto, re.S)
    return (m.group(1) if m else texto).strip() + "\n"


class Agentes:
    """Los nodos de los agentes, construidos sobre el mismo modelo (real o falso)."""

    def __init__(self, modelo):
        texto = StrOutputParser()
        self.planificar_cadena = PLANIFICADOR | modelo | texto
        self.implementar_cadena = IMPLEMENTADOR | modelo | texto
        self.probar_cadena = TESTER | modelo | texto
        self.revisar_cadena = REVISOR | modelo | texto

    def planificador(self, estado: Estado) -> dict:
        """Analiza el requisito y lo divide en tareas y casos (contrato Plan)."""
        comentario = "\n".join([estado.get("comentario", "")] + estado.get("errores", [])).strip()
        respuesta = self.planificar_cadena.invoke({
            "requisito": estado["requisito"], "comentario": comentario or "ninguno",
            "esquema": json.dumps(Plan.model_json_schema(), ensure_ascii=False)})
        try:
            plan = Plan.model_validate(extraer_json(respuesta))
        except (ValueError, ValidationError) as e:
            return {"fase": "plan", "plan": {}, "errores": [f"plan inválido: {e}"],
                    "rechazos": estado.get("rechazos", 0) + 1}
        return {"fase": "plan", "plan": plan.model_dump(), "errores": [], "aprobado": False}

    def implementador(self, estado: Estado) -> dict:
        """Escribe el módulo; seguridad.validar_codigo decide si se acepta."""
        respuesta = self.implementar_cadena.invoke({
            "plan": json.dumps(estado["plan"], ensure_ascii=False),
            "errores": "\n".join(estado.get("errores", [])) or "ninguno"})
        codigo = extraer_python(respuesta)
        problemas = validar_codigo(codigo, debe_definir=estado["plan"]["funcion"])
        if problemas:
            registrar("codigo_rechazado", agente="implementador", problemas=problemas)
        return {"fase": "codigo", "codigo": codigo, "errores": problemas, "ciclos": estado.get("ciclos", 0) + 1}

    def tester(self, estado: Estado) -> dict:
        """Escribe las pruebas y las ejecuta en el sandbox junto con el código."""
        respuesta = self.probar_cadena.invoke({"plan": json.dumps(estado["plan"], ensure_ascii=False)})
        pruebas = extraer_python(respuesta)
        problemas = validar_codigo(pruebas)
        if problemas:
            registrar("codigo_rechazado", agente="tester", problemas=problemas)
            return {"fase": "pruebas", "pruebas": pruebas, "resultado": {"ok": False, "salida": "\n".join(problemas)},
                    "errores": problemas}
        resultado = ejecutar_en_sandbox(estado["codigo"], pruebas)
        errores = [] if resultado["ok"] else [f"las pruebas fallaron:\n{resultado['salida']}"]
        return {"fase": "pruebas", "pruebas": pruebas, "resultado": resultado, "errores": errores}

    def revisor(self, estado: Estado) -> dict:
        """Revisa calidad y cobertura; el contrato Revision decide si el veredicto es coherente."""
        respuesta = self.revisar_cadena.invoke({
            "plan": json.dumps(estado["plan"], ensure_ascii=False), "codigo": estado["codigo"],
            "pruebas": estado["pruebas"], "resultado": estado["resultado"]["salida"],
            "esquema": json.dumps(Revision.model_json_schema(), ensure_ascii=False)})
        try:
            revision = Revision.model_validate(extraer_json(respuesta))
        except (ValueError, ValidationError) as e:
            revision = Revision(veredicto="cambios", hallazgos=[{"severidad": "alta", "descripcion": f"revisión inválida: {e}"}])
        errores = [h.descripcion for h in revision.hallazgos] if revision.veredicto == "cambios" else []
        return {"fase": "revision", "revision": revision.model_dump(), "errores": errores}