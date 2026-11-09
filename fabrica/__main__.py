"""Corre la fábrica desde la terminal.

    python -m fabrica requisitos/correo.md                 # te pregunta si apruebas el plan
    python -m fabrica requisitos/correo.md --aprobar       # aprobación por adelantado
    python -m fabrica --reanudar correo                    # retoma un hilo detenido (checkpoint)
"""
import argparse
import json
import sys
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from fabrica.grafo import construir_grafo
from fabrica.modelo import ModeloClaudeCLI

CHECKPOINTS = "checkpoints.sqlite"


def pedir_decision(pausa: dict, aprobar: bool) -> str:
    """Muestra el plan a la persona y devuelve su decisión."""
    print("\n--- Plan propuesto ---")
    print(json.dumps(pausa["plan"], ensure_ascii=False, indent=2))
    if aprobar:
        print("Aprobado por adelantado (--aprobar).")
        return "si"
    return input(pausa["pregunta"] + " > ")


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):                  # la consola de Windows usa cp1252 y no sabe escribir «→»
        flujo.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(prog="python -m fabrica", description="Fábrica mini con LangGraph y Claude Code")
    parser.add_argument("requisito", nargs="?", help="archivo .md con el requisito")
    parser.add_argument("--hilo", help="nombre del hilo (thread_id); por omisión, el nombre del archivo")
    parser.add_argument("--reanudar", metavar="HILO", help="retoma un hilo desde su último checkpoint")
    parser.add_argument("--aprobar", action="store_true", help="aprueba el plan sin preguntar")
    args = parser.parse_args()
    if not args.requisito and not args.reanudar:
        parser.error("indica un archivo de requisito o --reanudar HILO")

    hilo = args.reanudar or args.hilo or Path(args.requisito).stem
    try:
        return correr(args, hilo)
    except (EOFError, KeyboardInterrupt):
        print(f"\nPausado. El estado quedó guardado; continúa con: python -m fabrica --reanudar {hilo}")
        return 2


def correr(args, hilo: str) -> int:
    """Corre (o reanuda) el hilo hasta terminar, deteniéndose en cada pausa para la persona."""
    config = {"configurable": {"thread_id": hilo}}
    with SqliteSaver.from_conn_string(CHECKPOINTS) as checkpointer:
        app = construir_grafo(ModeloClaudeCLI(), checkpointer)
        if args.reanudar:
            instantanea = app.get_state(config)
            if not instantanea.next:
                print(f"El hilo «{hilo}» no tiene nada pendiente.")
                return 0
            print(f"Reanudando «{hilo}» en: {', '.join(instantanea.next)}")
            entrada = None
            if instantanea.interrupts:                       # se detuvo esperando a la persona
                entrada = Command(resume=pedir_decision(instantanea.interrupts[0].value, args.aprobar))
        else:
            entrada = {"requisito": Path(args.requisito).read_text(encoding="utf-8")}

        while True:
            for paso in app.stream(entrada, config, stream_mode="updates"):
                for nodo, cambios in paso.items():
                    if nodo == "__interrupt__":
                        continue
                    destino = (cambios or {}).get("siguiente")
                    print(f"[{nodo}]" + (f" → {destino}" if destino else ""))
            instantanea = app.get_state(config)
            if not instantanea.interrupts:
                break
            entrada = Command(resume=pedir_decision(instantanea.interrupts[0].value, args.aprobar))

        final = instantanea.values.get("final", "?")
        nombre = instantanea.values.get("plan", {}).get("funcion") or "sin_plan"
        print(f"\nEstado final: {final}. Reporte en salida/{nombre}/REPORTE.md")
        return 0 if final == "LISTA" else 1


if __name__ == "__main__":
    sys.exit(main())