# Reporte · es_correo_empleado_valido

**Estado final:** LISTA

## Requisito

# Requisito: validar el correo de un empleado

Necesito una función que reciba un correo y diga si es válido para registrar a un empleado.

- Debe terminar en @empresa.com (sin importar mayúsculas).
- La parte antes de la @ solo puede tener letras, números, puntos y guiones bajos, y no puede estar vacía.
- No puede tener espacios.

## Plan

`def es_correo_empleado_valido(correo: str) -> bool`

1. Verificar que el correo sea una cadena y no contenga espacios ni otros caracteres de espacio en blanco
1. Comprobar, sin distinguir mayúsculas, que termine en '@empresa.com'
1. Separar la parte local quitando el sufijo '@empresa.com' y verificar que no esté vacía
1. Verificar que la parte local no contenga otra '@' (solo una arroba en total)
1. Validar que cada carácter de la parte local sea letra (a-z, A-Z), número, punto o guion bajo
1. Devolver True solo si se cumplen todas las condiciones; en caso contrario, False

## Ciclos de corrección

2 de 3

## Pruebas

```
.................                                                        [100%]
17 passed in 0.09s
```

## Hallazgos del revisor

- **baja**: Las pruebas no cubren explícitamente un carácter Unicode que `lower()` podría mapear al sufijo (p. ej. 'K' Kelvin) ni letras no ASCII (p. ej. 'ñ') en la parte local; el código las rechaza correctamente por la comparación ASCII, pero convendría añadir una prueba que lo documente.
- **baja**: El plan pide verificar que la parte local no contenga otra '@'; el código lo hace, pero la prueba 'a@b@empresa.com' es el único caso. Podría añadirse un caso como 'ana@@empresa.com' para reforzar la cobertura.
