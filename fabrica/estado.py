"""El estado compartido del grafo y los contratos que validan lo que entrega cada agente.

El State de LangGraph es un conjunto de variables compartidas que viajan por el grafo: cada nodo lee
lo que necesita y devuelve solo lo que cambia. Los contratos Pydantic deciden si una entrega es válida
(el modelo propone y el código decide).
"""
from typing import Literal, TypedDict

from pydantic import BaseModel, Field, field_validator, model_validator


class Caso(BaseModel):
    """Un caso de prueba del plan: una llamada y el resultado esperado."""

    entrada: str = Field(description="Argumentos de la llamada en sintaxis Python, por ejemplo: 'ana@empresa.com'")
    esperado: str = Field(description="Resultado esperado en sintaxis Python, por ejemplo: True")


class Plan(BaseModel):
    """Lo que entrega el planificador: la función que hay que escribir, dividida en tareas."""

    funcion: str = Field(description="Nombre de la función en snake_case")
    firma: str = Field(description="Firma completa, por ejemplo: def es_correo_valido(correo: str) -> bool")
    tareas: list[str] = Field(min_length=1, max_length=8)
    casos: list[Caso] = Field(min_length=3, max_length=10)

    @field_validator("funcion")
    @classmethod
    def nombre_valido(cls, v: str) -> str:
        if not v.isidentifier() or not v.islower():
            raise ValueError("la función debe ser un identificador en snake_case")
        return v


class Hallazgo(BaseModel):
    """Un problema que encontró el revisor."""

    severidad: Literal["alta", "media", "baja"]
    descripcion: str


class Revision(BaseModel):
    """Lo que entrega el revisor. Con un hallazgo de severidad alta no se puede aprobar."""

    veredicto: Literal["aprobado", "cambios"]
    hallazgos: list[Hallazgo] = []

    @model_validator(mode="after")
    def coherente(self) -> "Revision":
        if self.veredicto == "aprobado" and any(h.severidad == "alta" for h in self.hallazgos):
            raise ValueError("no se puede aprobar con un hallazgo de severidad alta")
        return self


class Estado(TypedDict, total=False):
    """Variables compartidas que viajan por el grafo (la pizarra de la fábrica)."""

    requisito: str                 # entrada del usuario: contenido NO confiable
    fase: str                      # último paso completado: filtro, plan, aprobacion, codigo, pruebas, revision
    siguiente: str                 # a qué nodo manda el supervisor
    bloqueado: str                 # motivo si el filtro de seguridad detuvo el flujo
    plan: dict                     # Plan validado
    aprobado: bool                 # decisión de la persona sobre el plan (HITL)
    comentario: str                # comentario de la persona si rechazó el plan
    rechazos: int                  # cuántas veces se rechazó el plan
    codigo: str                    # módulo que escribió el implementador
    pruebas: str                   # pruebas pytest que escribió el tester
    resultado: dict                # {"ok": bool, "salida": str} de la ejecución en el sandbox
    revision: dict                 # Revision validada
    ciclos: int                    # ciclos de corrección usados (tope: MAX_CICLOS)
    errores: list[str]             # problemas de la última entrega, para que el agente corrija
    final: str                     # LISTA, BLOQUEADA o ESCALAR