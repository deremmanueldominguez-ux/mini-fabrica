import pytest
from modulo import es_correo_empleado_valido


def test_correo_simple_valido():
    assert es_correo_empleado_valido('ana@empresa.com') is True


def test_correo_con_mayusculas_puntos_guion_bajo_y_numeros():
    assert es_correo_empleado_valido('Ana.Lopez_01@EMPRESA.COM') is True


def test_parte_local_vacia():
    assert es_correo_empleado_valido('@empresa.com') is False


def test_dominio_distinto():
    assert es_correo_empleado_valido('ana@gmail.com') is False


def test_espacio_en_parte_local():
    assert es_correo_empleado_valido('ana lopez@empresa.com') is False


def test_guion_medio_no_permitido():
    assert es_correo_empleado_valido('ana-lopez@empresa.com') is False


def test_espacio_al_final():
    assert es_correo_empleado_valido('ana@empresa.com ') is False


def test_doble_arroba():
    assert es_correo_empleado_valido('a@b@empresa.com') is False


def test_sufijo_extra_despues_del_dominio():
    assert es_correo_empleado_valido('ana@empresa.com.mx') is False


# Casos de borde adicionales
def test_cadena_vacia():
    assert es_correo_empleado_valido('') is False


def test_solo_sufijo_en_mayusculas():
    assert es_correo_empleado_valido('@EMPRESA.COM') is False


def test_tabulador_en_correo():
    assert es_correo_empleado_valido('ana\t@empresa.com') is False


def test_salto_de_linea_al_final():
    assert es_correo_empleado_valido('ana@empresa.com\n') is False


def test_un_solo_caracter_en_parte_local():
    assert es_correo_empleado_valido('a@empresa.com') is True


def test_solo_numeros_y_puntos_en_parte_local():
    assert es_correo_empleado_valido('123.456@empresa.com') is True


def test_sin_arroba():
    assert es_correo_empleado_valido('empresa.com') is False


def test_entrada_no_cadena():
    assert es_correo_empleado_valido(None) is False
