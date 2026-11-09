"""Las defensas de la fábrica: entrada, salida, sandbox y bitácora de seguridad.

Ninguna capa basta sola (defensa en profundidad). Todas son código determinista: no dependen de que
el modelo se porte bien.
"""
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

BITACORA = Path(os.environ.get("FABRICA_BITACORA", "seguridad.jsonl"))
LARGO_MAXIMO = 2000          # caracteres del requisito
TIEMPO_SANDBOX = 20          # segundos para correr las pruebas

# Frases típicas de prompt injection: alguien intenta que el agente viole sus instrucciones.
PATRONES_INYECCION = [
    r"ignora\w* (todas )?(las )?instrucciones",
    r"ignore (all |the )?(previous |prior )?instructions",
    r"olvida\w* (todo|tus reglas|lo anterior)",
    r"eres ahora|act[uú]a como|you are now",
    r"system prompt|prompt del sistema",
    r"\.env\b|secret|contrase[nñ]a|password|api[_ ]?key|token",
    r"curl |wget |rm -rf|subprocess|os\.system",
]

# Lo que el código generado nunca puede importar ni llamar.
MODULOS_PROHIBIDOS = {"os", "sys", "subprocess", "socket", "shutil", "pathlib", "requests", "urllib",
                      "http", "ctypes", "importlib", "pickle", "multiprocessing", "threading"}
LLAMADAS_PROHIBIDAS = {"eval", "exec", "open", "compile", "__import__", "input", "globals", "locals", "getattr"}


def registrar(evento: str, **datos) -> None:
    """Agrega una línea a la bitácora de seguridad (JSON Lines)."""
    linea = {"hora": datetime.now(timezone.utc).isoformat(timespec="seconds"), "evento": evento, **datos}
    with BITACORA.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")


def filtrar_entrada(requisito: str) -> str | None:
    """Devuelve el motivo si el requisito es sospechoso, o None si puede pasar."""
    if not requisito.strip():
        return "el requisito está vacío"
    if len(requisito) > LARGO_MAXIMO:
        return f"el requisito pasa de {LARGO_MAXIMO} caracteres"
    texto = requisito.lower()
    for patron in PATRONES_INYECCION:
        if re.search(patron, texto):
            return f"posible prompt injection (patrón: {patron})"
    return None


def validar_codigo(codigo: str, debe_definir: str | None = None) -> list[str]:
    """Problemas del código generado: sintaxis, imports y llamadas peligrosas, y la función esperada."""
    try:
        arbol = ast.parse(codigo)
    except SyntaxError as e:
        return [f"el código no compila: {e}"]
    problemas = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres = [a.name.split(".")[0] for a in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            nombres = [(nodo.module or "").split(".")[0]]
        else:
            nombres = []
        for n in nombres:
            if n in MODULOS_PROHIBIDOS:
                problemas.append(f"import prohibido: {n}")
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name) and nodo.func.id in LLAMADAS_PROHIBIDAS:
            problemas.append(f"llamada prohibida: {nodo.func.id}()")
        if isinstance(nodo, ast.Attribute) and nodo.attr.startswith("__") and nodo.attr not in {"__init__", "__name__"}:
            problemas.append(f"atributo prohibido: {nodo.attr}")
    if debe_definir:
        definidas = {n.name for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef)}
        if debe_definir not in definidas:
            problemas.append(f"no define la función {debe_definir}")
    return problemas


def ejecutar_en_sandbox(codigo: str, pruebas: str) -> dict:
    """Corre las pruebas en una carpeta temporal, con intérprete aislado, sin red heredada y con tiempo límite."""
    with tempfile.TemporaryDirectory(prefix="fabrica_") as carpeta:
        Path(carpeta, "modulo.py").write_text(codigo, encoding="utf-8")
        Path(carpeta, "test_modulo.py").write_text(pruebas, encoding="utf-8")
        entorno = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1", "HOME": carpeta,
                   "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}   # sin plugins de terceros del venv
        if os.name == "nt":                                  # sin SYSTEMROOT, Windows no inicia Winsock (WinError 10106)
            entorno["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", r"C:\Windows")
        try:
            proc = subprocess.run([sys.executable, "-I", "-X", "utf8", "-m", "pytest", "-q", "-p", "no:cacheprovider", carpeta],
                                  cwd=carpeta, env=entorno, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=TIEMPO_SANDBOX)
            resultado = {"ok": proc.returncode == 0, "salida": (proc.stdout + proc.stderr)[-3000:]}
        except subprocess.TimeoutExpired:
            resultado = {"ok": False, "salida": f"las pruebas pasaron de {TIEMPO_SANDBOX} s y se detuvieron"}
    registrar("sandbox", ok=resultado["ok"])
    return resultado