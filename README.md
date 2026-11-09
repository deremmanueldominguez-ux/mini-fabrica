# Fábrica mini · LangGraph + Claude Code (sin API key)

Un sistema multiagente pequeño que toma un **requisito** y entrega **código + pruebas + documentación**,
con cuatro agentes especializados, un supervisor, checkpoints, una persona en el lazo y cinco capas de seguridad.
Los agentes usan **Claude Code en modo `claude -p`**, con tu sesión de `claude auth login`: no se usa `ANTHROPIC_API_KEY`.

```
requisito ─► filtro ─► SUPERVISOR ─┬─► planificador ─► (persona aprueba) ─► implementador ─► tester ─► revisor
                (seguridad)        │        ▲ rechazo (máx. 2)                  ▲  falla o cambios (máx. 3)  │
                                   └────────┴────────────────────────────────────┴────────────────────────────┘
                                                                                         ─► entregar (salida/)
```

## Setup

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
unset ANTHROPIC_API_KEY          # que Claude Code use tu suscripción
claude auth login                # solo la primera vez
```

## Uso

```bash
python -m fabrica requisitos/correo.md              # te muestra el plan y pregunta si lo apruebas
python -m fabrica requisitos/correo.md --aprobar    # aprobación por adelantado
python -m fabrica requisitos/envenenado.md          # prompt injection: termina BLOQUEADA
python -m fabrica --reanudar correo                 # retoma un hilo detenido desde su checkpoint
FABRICA_MODELO=haiku python -m fabrica ...          # modelo más rápido para practicar
```

El resultado queda en `salida/<funcion>/`: `modulo.py`, `test_modulo.py` y `REPORTE.md`.
La bitácora de seguridad queda en `seguridad.jsonl` y los checkpoints en `checkpoints.sqlite`.

## Pruebas

```bash
python -m pytest            # 10 pruebas con un modelo falso: no gastan cuota
```

## Estructura

| Archivo | Qué contiene | Concepto |
| --- | --- | --- |
| `fabrica/estado.py` | `Estado` (TypedDict) y los contratos `Plan`, `Revision` | State compartido, salidas estructuradas |
| `fabrica/modelo.py` | `ModeloClaudeCLI`: `claude -p` como chat model de LangChain | Abstracciones de LangChain |
| `fabrica/prompts.py` | Los cuatro prompts con `ChatPromptTemplate` | Prompt hardening |
| `fabrica/agentes.py` | Planificador, implementador, tester y revisor | Roles especializados |
| `fabrica/grafo.py` | Supervisor, `add_conditional_edges`, `interrupt()`, topes | Supervisor, HITL, ciclos con límite |
| `fabrica/seguridad.py` | Filtro de entrada, validación de código, sandbox, bitácora | Defensa en profundidad |
| `fabrica/__main__.py` | Línea de comandos con `SqliteSaver` y `--reanudar` | Checkpoints |
| `tests/test_fabrica.py` | El flujo completo con `FakeListChatModel` | Pruebas sin modelo |

## Las reglas

El modelo propone y el código decide · cada agente solo hace lo de su rol · todo bucle tiene un límite ·
una persona aprueba lo irreversible.