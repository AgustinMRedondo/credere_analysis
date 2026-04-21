"""Formulario de nueva operacion con todos los inputs editables."""

import reflex as rx

from credere.calcs.inputs import IAJD_POR_CCAA
from credere.state import AppState


def _num_input(label: str, value, on_change, step: float = 1000.0) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="medium"),
        rx.input(
            value=value,
            on_change=on_change,
            type="number",
            step=step,
            width="100%",
        ),
        spacing="1",
        align="stretch",
        width="100%",
    )


def _pct_input(label: str, value, on_change) -> rx.Component:
    return rx.vstack(
        rx.text(label, size="2", weight="medium"),
        rx.input(
            value=value,
            on_change=on_change,
            type="number",
            step=0.001,
            width="100%",
        ),
        spacing="1",
        align="stretch",
        width="100%",
    )


def new_project() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Nueva operacion", size="7"),
            rx.link("< Volver al panel", href="/"),
            rx.divider(),
            # --- Metadata ---------------------------------------------
            rx.heading("Metadata", size="4"),
            rx.grid(
                rx.input(
                    placeholder="Nombre del proyecto",
                    value=AppState.nombre,
                    on_change=AppState.set_nombre,
                ),
                rx.input(
                    placeholder="Localizacion",
                    value=AppState.localizacion,
                    on_change=AppState.set_localizacion,
                ),
                rx.select(
                    list(IAJD_POR_CCAA.keys()),
                    value=AppState.ccaa,
                    on_change=AppState.set_ccaa,
                ),
                rx.text_area(
                    placeholder="Descripcion",
                    value=AppState.descripcion,
                    on_change=AppState.set_descripcion,
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # --- Economicos -------------------------------------------
            rx.heading("Datos economicos del proyecto", size="4"),
            rx.grid(
                _num_input("Equity aportado (EUR)", AppState.equity, AppState.set_equity),
                _num_input("Coste adquisicion (EUR)", AppState.acq_cost, AppState.set_acq_cost),
                _num_input("Valor tasacion (EUR)", AppState.tasacion, AppState.set_tasacion),
                _num_input("Hard costs / CAPEX (EUR)", AppState.hard_costs, AppState.set_hard_costs),
                _num_input(
                    "Soft costs sin fee (EUR)",
                    AppState.soft_costs_sin_fee,
                    AppState.set_soft_costs_sin_fee,
                ),
                _num_input(
                    "Coste comercial (EUR)",
                    AppState.comercial_cost,
                    AppState.set_comercial_cost,
                ),
                _num_input(
                    "Ingresos esperados (EUR)",
                    AppState.ingresos_esperados,
                    AppState.set_ingresos_esperados,
                ),
                _num_input(
                    "Total unidades", AppState.total_unidades, AppState.set_total_unidades, step=1
                ),
                _num_input(
                    "Meses totales", AppState.meses_totales, AppState.set_meses_totales, step=1
                ),
                columns="3",
                spacing="3",
                width="100%",
            ),
            # --- Prestamo ---------------------------------------------
            rx.heading("Prestamo", size="4"),
            rx.grid(
                _num_input(
                    "Capital solicitado (EUR)",
                    AppState.capital_solicitado,
                    AppState.set_capital_solicitado,
                ),
                _num_input(
                    "Primera disposicion solicitada (EUR)",
                    AppState.primera_disposicion_solicitada,
                    AppState.set_primera_disposicion_solicitada,
                ),
                columns="2",
                spacing="3",
                width="100%",
            ),
            # --- Parametros (editables) -------------------------------
            rx.heading("Parametros (editables)", size="4"),
            rx.grid(
                _pct_input(
                    "Tasa anual deuda",
                    AppState.tasa_anual_deuda,
                    AppState.set_tasa_anual_deuda,
                ),
                _pct_input(
                    "Comision apertura",
                    AppState.comision_apertura,
                    AppState.set_comision_apertura,
                ),
                _pct_input("IAJD %", AppState.iajd_pct, AppState.set_iajd_pct),
                _pct_input("Notaria %", AppState.notaria_pct, AppState.set_notaria_pct),
                _pct_input("Minuta %", AppState.minuta_pct, AppState.set_minuta_pct),
                _pct_input("Registro %", AppState.registro_pct, AppState.set_registro_pct),
                _pct_input(
                    "Buffer legales (Credere)",
                    AppState.buffer_legales,
                    AppState.set_buffer_legales,
                ),
                _pct_input(
                    "Consultoria %", AppState.pct_consultoria, AppState.set_pct_consultoria
                ),
                columns="3",
                spacing="3",
                width="100%",
            ),
            # --- Acciones ---------------------------------------------
            rx.hstack(
                rx.button("Calcular", on_click=AppState.calcular, size="3"),
                rx.button(
                    "Analizar con Claude",
                    on_click=AppState.analizar_con_ia,
                    size="3",
                    variant="soft",
                ),
                rx.button(
                    "Guardar en Supabase",
                    on_click=AppState.guardar,
                    size="3",
                    color_scheme="green",
                ),
                spacing="3",
            ),
            rx.cond(
                AppState.error != "",
                rx.callout(AppState.error, icon="triangle_alert", color_scheme="red"),
            ),
            rx.cond(
                AppState.resultado,
                _panel_resultado(),
            ),
            spacing="4",
            align="stretch",
        ),
        padding="2em",
        max_width="1200px",
    )


def _panel_resultado() -> rx.Component:
    """Renderiza el resultado cuando existe."""
    # Accedemos via rx.Var -> sintaxis indexada sobre AppState.resultado
    pr = AppState.resultado["prestamo"]
    ra = AppState.resultado["ratios"]
    return rx.vstack(
        rx.divider(),
        rx.heading("Resultado", size="5"),
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.heading("Prestamo", size="3"),
                    rx.text("Capital solicitado: ", pr["capital_solicitado"]),
                    rx.text("Costes legales: ", pr["costes_legales"]["total"]),
                    rx.text("Prestamo total: ", pr["prestamo_total"]),
                    rx.text("1a disposicion total: ", pr["primera_disposicion_total"]),
                    rx.text("Consultoria: ", pr["consultoria"]),
                    align="start",
                ),
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Ratios", size="3"),
                    rx.text("EBIT: ", ra["EBIT"]),
                    rx.text("LTV: ", ra["LTV"]),
                    rx.text("LTC: ", ra["LTC"]),
                    rx.text("ROI promotor anual: ", ra["ROI_promotor_anualizado"]),
                    rx.text("ROI inversor anual: ", ra["ROI_inversor_anualizado"]),
                    align="start",
                ),
            ),
            columns="2",
            spacing="3",
            width="100%",
        ),
        align="stretch",
        width="100%",
    )
