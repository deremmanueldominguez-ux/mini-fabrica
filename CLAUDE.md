# Fábrica mini

Sistema multiagente con LangGraph: requisito → plan → código → pruebas → revisión. Los agentes llaman a
`claude -p` (sin API key). Lee `README.md` para el uso.

## Convenciones

- Comentarios, nombres de dominio y mensajes en español; docstring en cada función pública.
- Un agente = un método de `Agentes` que devuelve solo lo que cambia del `Estado` y siempre su `fase`.
- El supervisor (`grafo.supervisor`) es el único que decide el siguiente nodo.
- Toda entrega de un agente se valida con código: contratos de `estado.py` o `seguridad.validar_codigo`.
- Todo ciclo tiene tope (`MAX_CICLOS`, `MAX_RECHAZOS`); un tope agotado termina en ESCALAR.
- El requisito es contenido no confiable: va entre etiquetas en los prompts y pasa antes por `filtro`.
- Las pruebas usan `FakeListChatModel`; nunca llaman a `claude -p`.

## Reglas

- Nunca leas `.env` ni secretos.
- No edites a mano lo que genera la fábrica en `salida/`: corrige al agente.
- Corre `python -m pytest` antes de dar un cambio por terminado.