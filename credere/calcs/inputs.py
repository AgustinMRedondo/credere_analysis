"""Schemas Pydantic para inputs y outputs de los calculos.

Todos los parametros son editables: ParametrosGlobales lleva defaults del
modelo_basico.py historico + los nuevos de costes legales. Cada Proyecto
puede opcionalmente pisar cualquier parametro via `overrides`.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, computed_field


class ParametrosGlobales(BaseModel):
    """Parametros por defecto editables desde UI y persistibles en Supabase."""

    # --- Deuda -----------------------------------------------------------
    tasa_anual_deuda: float = Field(0.135, description="Tipo de interes anual")
    comision_apertura: float = Field(0.03, description="Comision apertura sobre deuda total")
    comision_apertura_terceros: float = Field(
        0.015,
        description="Fraccion de la comision apertura que va a terceros (no al inversor)",
    )

    # --- Credere fee (legacy, iterativo del modelo_basico) ---------------
    pct_levantamiento: float = Field(0.015, description="Comision levantamiento s/ deuda pre-fee")
    pct_credere_fee_hard: float = Field(0.012, description="Fee Credere sobre hard costs")
    pct_credere_fee_deuda: float = Field(0.003, description="Fee Credere sobre deuda pre-fee")

    # --- Costes legales (nuevo) -----------------------------------------
    iajd_pct: float = Field(0.015, description="IAJD (varia por CCAA)")
    notaria_pct: float = Field(0.005, description="Gastos notariales base")
    minuta_pct: float = Field(0.008, description="Minuta legal base")
    registro_pct: float = Field(0.002, description="Registro de la propiedad base")
    buffer_legales: float = Field(
        0.20,
        description="Buffer de seguridad de Credere sobre notaria, minuta y registro",
    )

    # --- Consultoria -----------------------------------------------------
    pct_consultoria: float = Field(0.028, description="Consultoria sobre prestamo total")


# Tabla IAJD por CCAA (% aplicado sobre capital solicitado).
# Editable: Madrid 0% es bonificacion sobre prestamos hipotecarios; confirmar con asesor.
IAJD_POR_CCAA: dict[str, float] = {
    "Andalucia": 0.012,
    "Aragon": 0.015,
    "Asturias": 0.012,
    "Baleares": 0.012,
    "Canarias": 0.010,
    "Cantabria": 0.015,
    "Castilla-La Mancha": 0.015,
    "Castilla y Leon": 0.015,
    "Cataluna": 0.015,
    "Ceuta": 0.005,
    "Extremadura": 0.015,
    "Galicia": 0.015,
    "La Rioja": 0.010,
    "Madrid": 0.000,
    "Melilla": 0.005,
    "Murcia": 0.015,
    "Navarra": 0.005,
    "Pais Vasco": 0.005,
    "Valencia": 0.015,
}


class Proyecto(BaseModel):
    """Inputs de una operacion concreta."""

    # --- Metadata --------------------------------------------------------
    id: Optional[str] = None
    nombre: str
    localizacion: str = ""
    ccaa: str = "Madrid"
    descripcion: str = ""
    fecha_creacion: date = Field(default_factory=date.today)
    fecha_financiacion: Optional[date] = None

    # --- Financieros del proyecto ---------------------------------------
    equity: float = Field(description="Equity aportado por el promotor")
    acq_cost: float = Field(description="Coste total de compra del activo")
    tasacion: float = Field(description="Valor de tasacion del activo (garantia)")
    hard_costs: float = Field(0.0, description="CAPEX / coste de obra")
    soft_costs_sin_fee: float = Field(0.0, description="Costes indirectos sin fee")
    comercial_cost: float = Field(0.0, description="Coste de comercializacion / agencia")
    ingresos_esperados: float = Field(description="Ingresos brutos esperados")
    total_unidades: int = Field(1, description="Numero de unidades a comercializar", ge=1)
    meses_totales: int = Field(12, description="Duracion del proyecto en meses", ge=1, le=36)

    # --- Prestamo --------------------------------------------------------
    capital_solicitado: float = Field(description="Capital que pide el promotor (= capital necesario)")
    primera_disposicion_solicitada: float = Field(
        description="Primera disposicion solicitada por el promotor (sin costes legales)",
    )

    # --- Overrides opcionales -------------------------------------------
    overrides: Optional[ParametrosGlobales] = None

    def params_efectivos(self, base: ParametrosGlobales) -> ParametrosGlobales:
        """Devuelve los parametros tras aplicar overrides (si los hay)."""
        if self.overrides is None:
            # Aun sin overrides explicitos, resolvemos IAJD por CCAA si aplica.
            if self.ccaa in IAJD_POR_CCAA:
                return base.model_copy(update={"iajd_pct": IAJD_POR_CCAA[self.ccaa]})
            return base
        return self.overrides


class CostesLegales(BaseModel):
    """Desglose de costes legales del prestamo (van en primera disposicion)."""

    iajd: float
    notaria: float
    minuta: float
    registro: float

    @computed_field  # type: ignore[misc]
    @property
    def total(self) -> float:
        return self.iajd + self.notaria + self.minuta + self.registro


class ResultadoDeuda(BaseModel):
    """Output del calculo iterativo de deuda + Credere fee."""

    deuda_total: float
    credere_fee: float
    comision_levantamiento: float
    iteraciones: int


class PrestamoCompleto(BaseModel):
    """Resumen del prestamo: deuda + costes legales + consultoria."""

    capital_solicitado: float
    deuda_iterativa: ResultadoDeuda
    costes_legales: CostesLegales
    prestamo_total: float
    primera_disposicion_solicitada: float
    primera_disposicion_total: float
    consultoria: float
    consultoria_inicial: float


class ResultadoCashflow(BaseModel):
    """Serie temporal mensual de flujos."""

    meses: int
    inflows: list[float]
    outflows: list[float]
    net_cashflow: list[float]
    deuda_mes: list[float]
    intereses_por_disposicion: list[float]
    intereses_acumulados: float
    deuda_acumulada: float
    comision_apertura: float


class Ratios(BaseModel):
    EBIT: float
    EBITDA: float
    ROI_promotor: float
    ROI_promotor_anualizado: float
    ROI_inversor: float
    ROI_inversor_anualizado: float
    LTV: float
    LTV_inicial: float
    LTC: float
    precio_unidad: float
    coste_real_deuda: float
    margen_ebit: float


class ResultadoCompleto(BaseModel):
    """Output del pipeline end-to-end para un proyecto."""

    proyecto: Proyecto
    params: ParametrosGlobales
    prestamo: PrestamoCompleto
    cashflow: ResultadoCashflow
    ratios: Ratios
