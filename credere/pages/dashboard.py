"""Pagina principal: listado de proyectos analizados + acceso rapido."""

import reflex as rx

from credere.state import AppState


def _fila_proyecto(p: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(p["nombre"]),
        rx.table.cell(p.get("localizacion", "")),
        rx.table.cell(p.get("ccaa", "")),
        rx.table.cell(p.get("fecha_creacion", "")),
        rx.table.cell(
            rx.link("Ver", href=f"/proyecto/{p['id']}", color_scheme="blue"),
        ),
    )


def dashboard() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Credere Analysis", size="8"),
            rx.text("Panel de operaciones inmobiliarias", color="gray"),
            rx.hstack(
                rx.button("+ Nueva operacion", on_click=rx.redirect("/nuevo"), size="3"),
                rx.button(
                    "Recargar",
                    on_click=AppState.cargar_proyectos,
                    variant="soft",
                    size="3",
                ),
            ),
            rx.cond(
                AppState.error != "",
                rx.callout(AppState.error, icon="triangle_alert", color_scheme="red"),
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Proyecto"),
                        rx.table.column_header_cell("Localizacion"),
                        rx.table.column_header_cell("CCAA"),
                        rx.table.column_header_cell("Fecha"),
                        rx.table.column_header_cell(""),
                    ),
                ),
                rx.table.body(
                    rx.foreach(AppState.proyectos, _fila_proyecto),
                ),
                width="100%",
            ),
            spacing="4",
            align="stretch",
        ),
        padding="2em",
        max_width="1200px",
        on_mount=AppState.cargar_proyectos,
    )
