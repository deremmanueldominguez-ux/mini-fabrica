"""El modelo de los agentes: Claude Code en modo `claude -p`, envuelto como un chat model de LangChain.

Envolverlo como `BaseChatModel` es justo el valor de LangChain: los agentes componen
`prompt | modelo | parser` sin saber qué hay detrás, y en las pruebas se cambia por un modelo falso.
No usa ANTHROPIC_API_KEY: corre con tu sesión de `claude auth login`.
"""
import os
import subprocess

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

TIEMPO_MAXIMO = 180  # segundos por llamada: todo tiene un límite


class ModeloClaudeCLI(BaseChatModel):
    """Chat model que responde llamando a `claude -p` sin herramientas."""

    modelo: str = os.environ.get("FABRICA_MODELO", "sonnet")

    @property
    def _llm_type(self) -> str:
        return "claude-cli"

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs) -> ChatResult:
        sistema = "\n".join(m.content for m in messages if isinstance(m, SystemMessage))
        usuario = "\n\n".join(m.content for m in messages if not isinstance(m, SystemMessage))
        entorno = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}  # usa la suscripción
        comando = ["claude", "-p", usuario, "--system-prompt", sistema,
                   "--tools", "",                       # el agente no ejecuta nada: solo responde texto
                   "--model", self.modelo, "--output-format", "text",
                   "--no-session-persistence", "--strict-mcp-config"]
        proc = subprocess.run(comando, capture_output=True, text=True, encoding="utf-8", timeout=TIEMPO_MAXIMO, env=entorno)
        if proc.returncode != 0:
            raise RuntimeError(f"claude -p falló ({proc.returncode}): {proc.stderr.strip()[:500]}")
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=proc.stdout.strip()))])