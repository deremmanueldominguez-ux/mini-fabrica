# Changelog

## 1.0.0 · 2026-10-31

- Grafo de LangGraph con supervisor y cuatro agentes: planificador, implementador, tester y revisor.
- Estado compartido (`Estado`) y contratos Pydantic `Plan` y `Revision`.
- Aprobación humana del plan con `interrupt()`; rechazo con comentario, máximo 2.
- Ciclo de corrección implementador → tester → revisor con tope `MAX_CICLOS = 3`.
- Checkpoints con `SqliteSaver` y `--reanudar` para retomar un hilo detenido.
- Seguridad: filtro de prompt injection, prompt hardening, validación del código con `ast`,
  sandbox para las pruebas (intérprete aislado, entorno mínimo, tiempo límite) y bitácora `seguridad.jsonl`.
- Modelo `ModeloClaudeCLI` sobre `claude -p` sin herramientas: no necesita API key.
- 10 pruebas con `FakeListChatModel`.