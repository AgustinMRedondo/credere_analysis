"""Tests de los calculos de prestamo y costes legales.

Incluye los 7 proyectos historicos del Excel como tests de regresion sobre
los costes legales (que son la parte totalmente determinista del modelo).
El IAJD y la consultoria tienen formula exacta; la notaria, minuta y registro
llevan el buffer del 20%. Los otros campos del Excel (Gastos asociados,
Prestamo total) los revisamos tras confirmar con el usuario las formulas
finales.
"""

import pytest

from credere.calcs import (
    ParametrosGlobales,
    Proyecto,
    calcular_costes_legales,
    calcular_deuda_iterativa,
    calcular_prestamo_completo,
)


# Defaults exactos del Excel "Informacion general"
PARAMS_EXCEL = ParametrosGlobales(
    tasa_anual_deuda=0.135,
    notaria_pct=0.005,
    minuta_pct=0.008,
    registro_pct=0.002,
    buffer_legales=0.20,
    pct_consultoria=0.028,
)


PROYECTOS_EXCEL = [
    # (nombre, capital, iajd_pct, meses, IAJD, Notaria, Minuta, Registro, Consultoria_total, Consult_inicial)
    ("Altabix", 300_000, 0.015, 9, 4_500, 1_800, 2_880, 720, 8_700, 2_900),
    ("Alcazares", 370_000, 0.015, 9, 5_550, 2_220, 3_552, 888, 11_000, 3_667),
    ("Puertas Coloradas", 490_000, 0.015, 12, 7_350, 2_940, 4_704, 1_176, 14_600, 3_650),
    ("Lanzarote Puerto", 560_000, 0.010, 12, 5_600, 3_360, 5_376, 1_344, 16_600, 4_150),
    ("Lote 3 Locales", 135_000, 0.015, 6, 2_025, 810, 1_296, 324, 4_000, 2_000),
    ("Gremis", 360_000, 0.015, 9, 5_400, 2_160, 3_456, 864, 10_500, 3_500),
    # Canillejas: el Excel muestra 0.8% en la columna IAJD% pero 1838/245000 = 0.75%.
    # Asumo que es un redondeo del display del Excel (%formatted) sobre una tasa real de 0.75%.
    # Revisar con Agustin si hubo deduccion especifica o si es tipo 0.75% real.
    ("Canillejas", 245_000, 0.0075, 9, 1_838, 1_470, 2_352, 588, 7_100, 2_367),
]


@pytest.mark.parametrize(
    "nombre,capital,iajd_pct,meses,iajd_esp,notaria_esp,minuta_esp,registro_esp,_c,_ci",
    PROYECTOS_EXCEL,
)
def test_costes_legales_excel(
    nombre, capital, iajd_pct, meses, iajd_esp, notaria_esp, minuta_esp, registro_esp, _c, _ci
):
    """Notaria = capital * 0.5% * 1.20. Minuta = capital * 0.8% * 1.20. etc."""
    params = PARAMS_EXCEL.model_copy(update={"iajd_pct": iajd_pct})
    cl = calcular_costes_legales(capital, params)
    # Tolerancia 5 EUR por redondeos del Excel (muestra enteros)
    assert abs(cl.iajd - iajd_esp) < 5, f"{nombre}: IAJD {cl.iajd} vs {iajd_esp}"
    assert abs(cl.notaria - notaria_esp) < 5, f"{nombre}: Notaria {cl.notaria} vs {notaria_esp}"
    assert abs(cl.minuta - minuta_esp) < 5, f"{nombre}: Minuta {cl.minuta} vs {minuta_esp}"
    assert abs(cl.registro - registro_esp) < 5, f"{nombre}: Registro {cl.registro} vs {registro_esp}"


def test_buffer_cero_notaria_es_base():
    """Sin buffer, notaria = capital * 0.5% exacto."""
    params = PARAMS_EXCEL.model_copy(update={"buffer_legales": 0.0})
    cl = calcular_costes_legales(300_000, params)
    assert cl.notaria == pytest.approx(300_000 * 0.005)
    assert cl.minuta == pytest.approx(300_000 * 0.008)
    assert cl.registro == pytest.approx(300_000 * 0.002)


def test_iajd_no_lleva_buffer():
    """El IAJD es impuesto; nunca se multiplica por (1 + buffer)."""
    params = PARAMS_EXCEL.model_copy(update={"buffer_legales": 1.0, "iajd_pct": 0.015})
    cl = calcular_costes_legales(100_000, params)
    assert cl.iajd == pytest.approx(1_500)  # NO 3000


def test_deuda_iterativa_converge():
    """El bucle de Credere fee debe converger en menos de 100 iteraciones."""
    p = Proyecto(
        nombre="Test",
        equity=50_000,
        acq_cost=200_000,
        tasacion=300_000,
        hard_costs=100_000,
        soft_costs_sin_fee=20_000,
        ingresos_esperados=400_000,
        total_unidades=2,
        meses_totales=12,
        capital_solicitado=250_000,
        primera_disposicion_solicitada=80_000,
    )
    d = calcular_deuda_iterativa(p, PARAMS_EXCEL)
    assert d.iteraciones < 100
    assert d.deuda_total > 0
    assert d.credere_fee > 0


def test_prestamo_completo_incluye_legales_en_primera_disposicion():
    p = Proyecto(
        nombre="Test",
        equity=50_000,
        acq_cost=200_000,
        tasacion=300_000,
        hard_costs=100_000,
        soft_costs_sin_fee=20_000,
        ingresos_esperados=400_000,
        total_unidades=2,
        meses_totales=12,
        capital_solicitado=250_000,
        primera_disposicion_solicitada=80_000,
    )
    pc = calcular_prestamo_completo(p, PARAMS_EXCEL)
    assert pc.primera_disposicion_total == pytest.approx(
        pc.primera_disposicion_solicitada + pc.costes_legales.total
    )
    assert pc.prestamo_total == pytest.approx(
        pc.deuda_iterativa.deuda_total + pc.costes_legales.total
    )


def test_consultoria_y_inicial():
    """Consultoria = 2.8% * prestamo_total. Inicial = consultoria * 3 / meses."""
    p = Proyecto(
        nombre="Test",
        equity=50_000,
        acq_cost=200_000,
        tasacion=300_000,
        hard_costs=100_000,
        soft_costs_sin_fee=20_000,
        ingresos_esperados=400_000,
        total_unidades=2,
        meses_totales=9,  # consult_inicial = consult / 3
        capital_solicitado=250_000,
        primera_disposicion_solicitada=80_000,
    )
    pc = calcular_prestamo_completo(p, PARAMS_EXCEL)
    assert pc.consultoria == pytest.approx(pc.prestamo_total * 0.028)
    assert pc.consultoria_inicial == pytest.approx(pc.consultoria * 3 / 9)
