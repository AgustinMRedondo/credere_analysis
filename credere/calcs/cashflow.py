"""Cashflow mensual del proyecto: outflows (disposiciones), inflows (equity + deuda),
intereses por disposicion y repago final.

Port directo del bloque de `modelo_basico.py` (lineas 76-119). La tasa de interes
es SIMPLE sobre disposiciones puntuales hasta el mes final del proyecto.
"""

from credere.calcs.inputs import (
    ParametrosGlobales,
    PrestamoCompleto,
    Proyecto,
    ResultadoCashflow,
)


def calcular_cashflow(
    proyecto: Proyecto,
    prestamo: PrestamoCompleto,
    params: ParametrosGlobales,
) -> ResultadoCashflow:
    meses = proyecto.meses_totales
    if meses < 2:
        raise ValueError("meses_totales debe ser >= 2 para el modelo de disposiciones")

    # === 1. Outflows: acq_cost en mes 0 + disposiciones medias de hard/soft ===
    disposiciones_totales = meses - 1  # el ultimo mes es repago
    soft_costs_con_fee = proyecto.soft_costs_sin_fee + prestamo.deuda_iterativa.credere_fee
    hard_mensual = proyecto.hard_costs / disposiciones_totales
    soft_mensual = soft_costs_con_fee / disposiciones_totales

    outflows = [0.0] * meses
    outflows[0] = proyecto.acq_cost + hard_mensual + soft_mensual
    for m in range(1, disposiciones_totales):
        outflows[m] = hard_mensual + soft_mensual
    # outflows[-1] se rellena abajo con el repago

    # === 2. Inflows e identificacion de deuda por mes ===
    inflows = [0.0] * meses
    deuda_mes = [0.0] * meses
    inflows[0] = proyecto.equity

    for m in range(meses):
        net = sum(inflows[: m + 1]) - sum(outflows[: m + 1])
        if net < 0:
            deuda = -net
            inflows[m] += deuda
            deuda_mes[m] = deuda
    inflows[-1] = proyecto.ingresos_esperados

    # === 3. Intereses simples por disposicion hasta fin de proyecto ===
    tasa_mensual = params.tasa_anual_deuda / 12
    intereses_por_disposicion = [0.0] * meses
    deuda_acumulada = 0.0
    for m in range(meses):
        if deuda_mes[m] > 0:
            meses_restantes = meses - m
            intereses_por_disposicion[m] = deuda_mes[m] * tasa_mensual * meses_restantes
            deuda_acumulada += deuda_mes[m]
    intereses_acumulados = sum(intereses_por_disposicion)

    # === 4. Comision apertura + repago final ===
    comision_apertura = prestamo.deuda_iterativa.deuda_total * params.comision_apertura
    outflows[-1] += (
        deuda_acumulada
        + intereses_acumulados
        + comision_apertura
        + proyecto.comercial_cost
    )

    net_cashflow = [inflows[m] - outflows[m] for m in range(meses)]

    return ResultadoCashflow(
        meses=meses,
        inflows=inflows,
        outflows=outflows,
        net_cashflow=net_cashflow,
        deuda_mes=deuda_mes,
        intereses_por_disposicion=intereses_por_disposicion,
        intereses_acumulados=intereses_acumulados,
        deuda_acumulada=deuda_acumulada,
        comision_apertura=comision_apertura,
    )
