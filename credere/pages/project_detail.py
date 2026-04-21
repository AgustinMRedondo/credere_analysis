"""Pagina de detalle de un proyecto. TODO: cargar desde Supabase por id."""

import reflex as rx


def project_detail() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.link("< Volver al panel", href="/"),
            rx.heading("Detalle de proyecto", size="7"),
            rx.text(
                "TODO: leer id de la ruta dinamica, cargar proyecto + ultimo "
                "resultado de Supabase, renderizar ficha completa + historial "
                "de analisis IA + boton de exportar PDF.",
                color="gray",
            ),
            spacing="3",
        ),
        padding="2em",
    )
