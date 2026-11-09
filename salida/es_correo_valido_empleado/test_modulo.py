import pytest
from modulo import es_correo_valido_empleado


def test_correo_simple_valido():
    assert es_correo_valido_empleado('ana@empresa.com') is True


def test_correo_con_mayusculas_punto_y_guion_bajo():
    assert es_correo_valido_empleado('Ana.Lopez_01@EMPRESA.COM') is True


def test_parte_local_vacia():
    assert es_correo_valido_empleado('@empresa.com') is False


def test_espacio_interno():
    assert es_correo_valido_empleado('ana lopez@empresa.com') is False


def test_guion_medio_no_permitido():
    assert es_correo_valido_empleado('ana-lopez@empresa.com') is False


def test_dominio_distinto():
    assert es_correo_valido_empleado('ana@gmail.com') is False


def test_espacio_al_final():
    assert es_correo_valido_empleado('ana@empresa.com ') is False


def test_doble_arroba():
    assert es_correo_valido_empleado('a@b@empresa.com') is False


def test_sufijo_extra():
    assert es_correo_valido_empleado('ana@empresa.com.mx') is False


def test_cadena_vacia():
    assert es_correo_valido_empleado('') is False


# Casos de borde adicionales
def test_no_es_cadena():
    assert es_correo_valido_empleado(None) is False
    assert es_correo_valido_empleado(123) is False


def test_tabulador_y_salto_de_linea():
    assert es_correo_valido_empleado('ana\t@empresa.com') is False
    assert es_correo_valido_empleado('ana@empresa.com\n') is False


def test_caracter_no_ascii():
    assert es_correo_valido_empleado('añá@empresa.com') is False


def test_un_solo_caracter_local():
    assert es_correo_valido_empleado('a@empresa.com') is True


def test_solo_sufijo_sin_arroba_inicial():
    assert es_correo_valido_empleado('empresa.com') is False
