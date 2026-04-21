"""Calculo del prestamo: costes legales con buffer, deuda iterativa (Credere fee),
consultoria, y agregados para la primera disposicion.

Las formulas de `calcular_deuda_iterativa` son port exacto de `modelo_basico.py`
(lineas 55-71 del repo v1). La capa de `calcular_costes_legales` es nueva:
el 20% de buffer aplica a notaria, minuta y registro; el IAJD va al valor real
porque es impuesto (lo paga Hacienda, no lo reservamos nosotros).
"""

from credere.calcs.inputs import (
    CostesLegales,
    ParametrosGlobales,
    PrestamoCompleto,
    Proyecto,
    ResultadoDeuda,
)


def calcular_costes_legales(
    capital_solicitado: float,
    params: ParametrosGlobales,
) -> CostesLegales:
    """
    Costes legales que el promotor paga en la primera disposicion.

    IAJD es impuesto real (sin buffer). Notaria, minuta y registro llevan buffer
    de Credere para cubrir desviaciones y constituir margen de seguridad.
    """
    buffer = 1 + params.buffer_legales
    iajd = capital_solicitado * params.iajd_pct
    notaria = capital_solicitado * params.notaria_pct * buffer
    minuta = capital_solicitado * params.minuta_pct * buffer
    registro = capital_solicitado * params.registro_pct * buffer
    return CostesLegales(iajd=iajd, notaria=notaria, minuta=minuta, registro=registro)


def calcular_deuda_iterativa(
    proyecto: Proyecto,
    params: ParametrosGlobales,
) -> ResultadoDeuda:
    """
    Port exacto del bucle de modelo_basico.py: iteramos hasta que la deuda
    total converja (tolerancia 0,01 EUR) porque el Credere fee se calcula
    sobre la deuda que a su vez depende del fee.
    """
    deuda_total = 0.0
    credere_fee = 0.0
    com_lev = 0.0
    tolerancia = 1.0
    iteraciones = 0
    MAX_ITER = 100

    while tolerancia > 0.01 and iteraciones < MAX_ITER:
        deuda_pre = (
            proyecto.hard_costs
            + proyecto.soft_costs_sin_fee
            + proyecto.acq_cost
            - proyecto.equity
        )
        com_lev = params.pct_levantamiento * deuda_pre
        credere_fee = (
            params.pct_credere_fee_hard * proyecto.hard_costs
            + params.pct_credere_fee_deuda * deuda_pre
            + com_lev
        )
        deuda_nueva = deuda_pre + credere_fee
        tolerancia = abs(deuda_nueva - deuda_total)
        deuda_total = deuda_nueva
        iteraciones += 1

    return ResultadoDeuda(
        deuda_total=deuda_total,
        credere_fee=credere_fee,
        comision_levantamiento=com_lev,
        iteraciones=iteraciones,
    )


def calcular_prestamo_completo(
    proyecto: Proyecto,
    params: ParametrosGlobales | None = None,
) -> PrestamoCompleto:
    """
    Orquesta: deuda iterativa + costes legales + consultoria.

    El prestamo total = deuda (que cubre la operacion) + costes legales
    (que se pagan en primera disposicion y por tanto tambien se financian).
    La consultoria se calcula sobre el prestamo TOTAL (patron verificado
    en los 7 proyectos historicos del Excel: 2,8% sobre prestamo total,
    no sobre capital solicitado).
    """
    params = proyecto.params_efectivos(params or ParametrosGlobales())

    deuda = calcular_deuda_iterativa(proyecto, params)
    costes_legales = calcular_costes_legales(proyecto.capital_solicitado, params)

    # Prestamo total = deuda del proyecto + costes legales a financiar
    prestamo_total = deuda.deuda_total + costes_legales.total
    primera_disposicion_total = (
        proyecto.primera_disposicion_solicitada + costes_legales.total
    )

    # Consultoria: 2,8% s/ prestamo total; inicial = consultoria * 3 / meses
    consultoria = prestamo_total * params.pct_consultoria
    consultoria_inicial = (
        consultoria * 3 / proyecto.meses_totales if proyecto.meses_totales > 0 else 0.0
    )

    return PrestamoCompleto(
        capital_solicitado=proyecto.capital_solicitado,
        deuda_iterativa=deuda,
        costes_legales=costes_legales,
        prestamo_total=prestamo_total,
        primera_disposicion_solicitada=proyecto.primera_disposicion_solicitada,
        primera_disposicion_total=primera_disposicion_total,
        consultoria=consultoria,
        consultoria_inicial=consultoria_inicial,
    )
