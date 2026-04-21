"""Tests de cashflow y ratios."""

import pytest

from credere.calcs import (
    ParametrosGlobales,
    Proyecto,
    analizar_proyecto,
)


@pytest.fixture
def proyecto_base():
    return Proyecto(
        nombre="Test",
        equity=100_000,
        acq_cost=300_000,
        tasacion=500_000,
        hard_costs=150_000,
        soft_costs_sin_fee=30_000,
        comercial_cost=10_000,
        ingresos_esperados=600_000,
        total_unidades=2,
        meses_totales=12,
        capital_solicitado=400_000,
        primera_disposicion_solicitada=150_000,
    )


def test_cashflow_longitud_meses(proyecto_base):
    r = analizar_proyecto(proyecto_base)
    assert len(r.cashflow.inflows) == 12
    assert len(r.cashflow.outflows) == 12
    assert len(r.cashflow.net_cashflow) == 12


def test_equity_en_mes_cero(proyecto_base):
    r = analizar_proyecto(proyecto_base)
    # inflows[0] >= equity (puede llevar deuda encima)
    assert r.cashflow.inflows[0] >= proyecto_base.equity


def test_ingresos_en_mes_final(proyecto_base):
    r = analizar_proyecto(proyecto_base)
    assert r.cashflow.inflows[-1] == pytest.approx(proyecto_base.ingresos_esperados)


def test_ratios_signo_basico(proyecto_base):
    """Con numeros razonables: EBITDA > 0, LTV entre 0 y 2, LTC > 0."""
    r = analizar_proyecto(proyecto_base)
    assert r.ratios.EBITDA != 0
    assert 0 < r.ratios.LTV < 2
    assert r.ratios.LTC > 0


def test_comision_apertura_es_pct_deuda(proyecto_base):
    r = analizar_proyecto(proyecto_base)
    # comision_apertura = deuda_total * 3% (default)
    esperado = r.prestamo.deuda_iterativa.deuda_total * 0.03
    assert r.cashflow.comision_apertura == pytest.approx(esperado)


def test_params_override_por_ccaa():
    """Madrid tiene IAJD 0%; Cataluna 1.5%."""
    p = Proyecto(
        nombre="Test", ccaa="Madrid",
        equity=100_000, acq_cost=300_000, tasacion=500_000,
        hard_costs=150_000, soft_costs_sin_fee=30_000,
        ingresos_esperados=600_000, total_unidades=2, meses_totales=12,
        capital_solicitado=400_000, primera_disposicion_solicitada=150_000,
    )
    r_madrid = analizar_proyecto(p, ParametrosGlobales())
    assert r_madrid.prestamo.costes_legales.iajd == 0.0

    p2 = p.model_copy(update={"ccaa": "Cataluna"})
    r_cat = analizar_proyecto(p2, ParametrosGlobales())
    assert r_cat.prestamo.costes_legales.iajd == pytest.approx(400_000 * 0.015)
