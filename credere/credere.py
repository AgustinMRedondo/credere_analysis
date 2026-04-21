"""Reflex app entrypoint. Registra rutas y arranca la app."""

import reflex as rx

from credere.pages import dashboard, new_project, project_detail

app = rx.App(
    theme=rx.theme(appearance="light", accent_color="blue"),
)
app.add_page(dashboard, route="/", title="Credere Analysis")
app.add_page(new_project, route="/nuevo", title="Nueva operacion | Credere")
app.add_page(project_detail, route="/proyecto/[id]", title="Proyecto | Credere")
