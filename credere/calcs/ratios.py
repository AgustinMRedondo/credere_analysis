"""Ratios financieros: EBIT/EBITDA, ROIs, LTV, LTC, precio/unidad.

Port de `modelo_basico.py` lineas 118-137. Un ajuste: el EBIT aqui se
calcula como net_cashflow[-1] - equity (igual que el original) y NO incluye
en el total_costs_sin_deuda la consultoria ni los costes legales nuevos,
porque esos se consideran costes de financiacion (aparte del EBITDA).
Si quieres EBITDA all-in, se puede agregar en el engine.
"""

from credere.calcs.inputs import (
    ParametrosGlobales,
    PrestamoCompleto,
    Proyecto,
    Ratios,
    ResultadoCashflow,
)


def calcular_ratios(
    proyecto: Proyecto,
    prestamo: PrestamoCompleto,
    cashflow: ResultadoCashflow,
    params: ParametrosGlobales,
) -> Ratios:
    soft_costs_con_fee = proyecto.soft_costs_sin_fee + prestamo.deuda_iterativa.credere_fee
    total_costs_sin_deuda = (
        proyecto.hard_costs
        + soft_costs_con_fee
        + proyecto.acq_cost
        + proyecto.comercial_cost
    )

    EBITDA = proyecto.ingresos_esperados - total_costs_sin_deuda
    intereses_totales = cashflow.intereses_acumulados + cashflow.comision_apertura
    EBIT = EBITDA - intereses_totales

    # ROIs
    ROI_promotor = EBIT / proyecto.equity if proyecto.equity else 0.0
    ROI_promotor_anualizado = ROI_promotor * 12 / proyecto.meses_totales

    comision_apertura_terceros = (
        cashflow.deuda_acumulada * params.comision_apertura_terceros
    )
    free_cash_inversor = (
        cashflow.intereses_acumulados + cashflow.comision_apertura - comision_apertura_terceros
    )
    deuda_total = prestamo.deuda_iterativa.deuda_total
    ROI_inversor = free_cash_inversor / deuda_total if deuda_total else 0.0
    ROI_inversor_anualizado = ROI_inversor * 12 / proyecto.meses_totales

    # LTVs y LTC
    LTV = deuda_total / proyecto.ingresos_esperados if proyecto.ingresos_esperados else 0.0
    LTV_inicial = (
        (cashflow.inflows[0] - proyecto.equity) / proyecto.tasacion
        if proyecto.tasacion
        else 0.0
    )
    LTC = deuda_total / total_costs_sin_deuda if total_costs_sin_deuda else 0.0

    precio_unidad = (
        proyecto.ingresos_esperados / proyecto.total_unidades
        if proyecto.total_unidades
        else 0.0
    )

    coste_real_deuda = (
        (intereses_totales + prestamo.deuda_iterativa.credere_fee) / deuda_total
        if deuda_total
        else 0.0
    )
    margen_ebit = EBIT / proyecto.ingresos_esperados if proyecto.ingresos_esperados else 0.0

    return Ratios(
        EBIT=EBIT,
        EBITDA=EBITDA,
        ROI_promotor=ROI_promotor,
        ROI_promotor_anualizado=ROI_promotor_anualizado,
        ROI_inversor=ROI_inversor,
        ROI_inversor_anualizado=ROI_inversor_anualizado,
        LTV=LTV,
        LTV_inicial=LTV_inicial,
        LTC=LTC,
        precio_unidad=precio_unidad,
        coste_real_deuda=coste_real_deuda,
        margen_ebit=margen_ebit,
    )
