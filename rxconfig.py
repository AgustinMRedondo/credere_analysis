import reflex as rx

config = rx.Config(
    app_name="credere",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
    tailwind={},
)
