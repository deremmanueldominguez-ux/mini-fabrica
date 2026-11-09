SUFIJO_EMPRESA: str = "@empresa.com"


def _caracter_local_valido(caracter: str) -> bool:
    """Indica si un carácter es letra ASCII, dígito ASCII, punto o guion bajo."""
    return (
        ("a" <= caracter <= "z")
        or ("A" <= caracter <= "Z")
        or ("0" <= caracter <= "9")
        or caracter in "._"
    )


def es_correo_empleado_valido(correo: str) -> bool:
    """Valida un correo de empleado del dominio '@empresa.com'.

    Reglas:
    - Debe ser una cadena sin ningún carácter de espacio en blanco.
    - Debe terminar en '@empresa.com' (sin distinguir mayúsculas).
    - La parte local no puede estar vacía ni contener otra '@'.
    - La parte local solo admite letras, números, punto o guion bajo.

    Args:
        correo: Cadena con el correo a validar.

    Returns:
        True si el correo cumple todas las condiciones; False en otro caso.
    """
    if not isinstance(correo, str):
        return False
    if any(c.isspace() for c in correo):
        return False
    if not correo.lower().endswith(SUFIJO_EMPRESA):
        return False
    parte_local = correo[: len(correo) - len(SUFIJO_EMPRESA)]
    if not parte_local:
        return False
    if "@" in parte_local:
        return False
    return all(_caracter_local_valido(c) for c in parte_local)
