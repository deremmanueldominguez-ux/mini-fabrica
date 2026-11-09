from typing import Final

_SUFIJO: Final[str] = "@empresa.com"
_PERMITIDOS: Final[frozenset] = frozenset(
    "abcdefghijklmnopqrstuvwxyz0123456789._"
)


def es_correo_valido_empleado(correo: str) -> bool:
    """Indica si un correo es válido para un empleado.

    Reglas: debe ser una cadena sin espacios en blanco, terminar en
    @empresa.com (sin distinguir mayúsculas), y su parte local no debe estar
    vacía ni contener '@'; solo se admiten letras ASCII, dígitos, punto y
    guion bajo.

    Args:
        correo: Cadena con el correo a validar.

    Returns:
        True si cumple todas las condiciones, False en caso contrario.
    """
    if not isinstance(correo, str):
        return False
    if any(c.isspace() for c in correo):
        return False

    texto = correo.lower()
    if not texto.endswith(_SUFIJO):
        return False

    local = texto[: -len(_SUFIJO)]
    if not local or "@" in local:
        return False

    return all(c in _PERMITIDOS for c in local)
