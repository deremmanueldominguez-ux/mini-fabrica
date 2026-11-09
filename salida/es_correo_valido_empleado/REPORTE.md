# Reporte · es_correo_valido_empleado

**Estado final:** LISTA

## Requisito

# Requisito: validar el correo de un empleado

Necesito una función que reciba un correo y diga si es válido para registrar a un empleado.

- Debe terminar en @empresa.com (sin importar mayúsculas).
- La parte antes de la @ solo puede tener letras, números, puntos y guiones bajos, y no puede estar vacía.
- No puede tener espacios.

## Plan

`def es_correo_valido_empleado(correo: str) -> bool`

1. Verificar que el correo sea una cadena y no contenga espacios ni otros espacios en blanco
1. Pasar el correo a minúsculas para ignorar mayúsculas en la comparación
1. Comprobar que termine exactamente en @empresa.com
1. Separar la parte local quitando el sufijo @empresa.com
1. Verificar que la parte local no esté vacía y no contenga otra @
1. Validar que cada carácter de la parte local sea letra, número, punto o guion bajo (ASCII)
1. Devolver True solo si todas las condiciones se cumplen, de lo contrario False

## Ciclos de corrección

3 de 3

## Pruebas

```
...............                                                          [100%]
15 passed in 0.07s
```

## Hallazgos del revisor

- **media**: El plan pide validar la parte local como ASCII, pero el código aplica lower() antes de validar. El signo Kelvin (U+212A) se convierte en 'k' ASCII, así que 'anaK@empresa.com' devuelve True aunque contiene un carácter no ASCII. Conviene validar los caracteres originales, por ejemplo con correo.isascii(), o comprobar el ASCII antes de pasar a minúsculas.
- **baja**: Ninguna prueba cubre caracteres cuyo lower() produce ASCII (como el signo Kelvin). La prueba de no ASCII solo usa 'añá', que no detecta este caso.
- **baja**: _PERMITIDOS está anotado como Final[frozenset] sin parametrizar el tipo. Sería más claro usar Final[frozenset[str]].
