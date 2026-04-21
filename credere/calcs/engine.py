"""Orquestador end-to-end: proyecto + parametros -> ResultadoCompleto.

Llamar a `analizar_proyecto(proyecto)` desde la UI y desde la capa AI.
"""

from credere.calcs.cashflow import calcular_cashflow
from credere.calcs.inputs import (
    ParametrosGlobales,
    Proyecto,
    ResultadoCompleto,
)
from credere.calcs.loan import calcular_prestamo_completo
from credere.calcs.ratios import calcular_ratios


def analizar_proyecto(
    proyecto: Proyecto,
    params: ParametrosGlobales | None = None,
) -> ResultadoCompleto:
    """Pipeline completo: prestamo -> cashflow -> ratios."""
    params_base = params or ParametrosGlobales()
    params_efectivos = proyecto.params_efectivos(params_base)

    prestamo = calcular_prestamo_completo(proyecto, params_efectivos)
    cashflow = calcular_cashflow(proyecto, prestamo, params_efectivos)
    ratios = calcular_ratios(proyecto, prestamo, cashflow, params_efectivos)

    return ResultadoCompleto(
        proyecto=proyecto,
        params=params_efectivos,
        prestamo=prestamo,
        cashflow=cashflow,
        ratios=ratios,
    )
