"""Modelos Pydantic de las filas en Supabase.

Se mapean 1:1 a las tablas definidas en migrations/001_initial.sql.
Serializacion JSON transparente para columnas `jsonb`.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel


class ParametrosRow(BaseModel):
    """Tabla `parametros_globales` - unico registro editable por el usuario."""

    id: int = 1
    payload: dict[str, Any]  # ParametrosGlobales.model_dump()
    updated_at: Optional[datetime] = None


class ProyectoRow(BaseModel):
    """Tabla `proyectos` - una fila por operacion analizada."""

    id: Optional[str] = None  # uuid
    nombre: str
    localizacion: str
    ccaa: str
    descripcion: str
    fecha_creacion: date
    fecha_financiacion: Optional[date] = None
    payload: dict[str, Any]  # Proyecto.model_dump() completo
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ResultadoRow(BaseModel):
    """Tabla `resultados` - snapshot inmutable de cada analisis ejecutado."""

    id: Optional[str] = None
    proyecto_id: str
    params_snapshot: dict[str, Any]
    prestamo: dict[str, Any]
    cashflow: dict[str, Any]
    ratios: dict[str, Any]
    analisis_mercado: Optional[dict[str, Any]] = None
    scoring: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
