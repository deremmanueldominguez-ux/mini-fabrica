# Reporte · es_correo_valido

**Estado final:** ESCALAR

## Requisito

Valida correos de @empresa.com

## Plan

`def es_correo_valido(correo: str) -> bool`

1. Normalizar a minúsculas
1. Validar el dominio
1. Validar la parte local

## Ciclos de corrección

3 de 3

## Pruebas

```
Error while loading plugin "pytest11".
D:\Next-Gen Coding 2026\Modulo 3\fabrica_mini\.venv\Lib\site-packages\anyio\pytest_plugin.py:309: in <module>
    @pytest.fixture(scope="module", params=get_available_backends())
                                           ^^^^^^^^^^^^^^^^^^^^^^^^
D:\Next-Gen Coding 2026\Modulo 3\fabrica_mini\.venv\Lib\site-packages\anyio\_core\_eventloop.py:157: in get_available_backends
    get_async_backend(backend_name)
D:\Next-Gen Coding 2026\Modulo 3\fabrica_mini\.venv\Lib\site-packages\anyio\_core\_eventloop.py:210: in get_async_backend
    module = import_module(f"anyio._backends._{asynclib_name}")
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
D:\Next-Gen Coding 2026\Modulo 3\fabrica_mini\.venv\Lib\site-packages\anyio\_backends\_asyncio.py:4: in <module>
    import asyncio
..\..\..\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\asyncio\__init__.py:43: in <module>
    from .windows_events import *
..\..\..\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\asyncio\windows_events.py:8: in <module>
    import _overlapped
E   OSError: [WinError 10106] The requested service provider could not be loaded or initialized
```

## Pendiente para una persona

- no define la función es_correo_valido
