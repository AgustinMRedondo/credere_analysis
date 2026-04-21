"""Estado global de la app Reflex.

Mantiene los parametros globales en memoria + el proyecto en edicion + la
ultima lista de proyectos leida de Supabase.
"""

from __future__ import annotations

from typing import Any, Optional

import reflex as rx

from credere.calcs import (
    ParametrosGlobales,
    Proyecto,
    ResultadoCompleto,
    analizar_proyecto,
)


class AppState(rx.State):
    """Estado compartido entre paginas."""

    # --- Parametros globales (editables) ---------------------------------
    tasa_anual_deuda: float = 0.135
    comision_apertura: float = 0.03
    iajd_pct: float = 0.015
    notaria_pct: float = 0.005
    minuta_pct: float = 0.008
    registro_pct: float = 0.002
    buffer_legales: float = 0.20
    pct_consultoria: float = 0.028
    pct_credere_fee_hard: float = 0.012
    pct_credere_fee_deuda: float = 0.003
    pct_levantamiento: float = 0.015
    comision_apertura_terceros: float = 0.015

    # --- Proyecto en edicion (form inputs crudos) ------------------------
    nombre: str = ""
    localizacion: str = ""
    ccaa: str = "Madrid"
    descripcion: str = ""
    equity: float = 0.0
    acq_cost: float = 0.0
    tasacion: float = 0.0
    hard_costs: float = 0.0
    soft_costs_sin_fee: float = 0.0
    comercial_cost: float = 0.0
    ingresos_esperados: float = 0.0
    total_unidades: int = 1
    meses_totales: int = 12
    capital_solicitado: float = 0.0
    primera_disposicion_solicitada: float = 0.0

    # --- Resultados del calculo (dict serializable para Reflex) ---------
    resultado: Optional[dict[str, Any]] = None
    error: str = ""

    # --- Listado --------------------------------------------------------
    proyectos: list[dict[str, Any]] = []

    def _build_params(self) -> ParametrosGlobales:
        return ParametrosGlobales(
            tasa_anual_deuda=self.tasa_anual_deuda,
            comision_apertura=self.comision_apertura,
            comision_apertura_terceros=self.comision_apertura_terceros,
            pct_levantamiento=self.pct_levantamiento,
            pct_credere_fee_hard=self.pct_credere_fee_hard,
            pct_credere_fee_deuda=self.pct_credere_fee_deuda,
            iajd_pct=self.iajd_pct,
            notaria_pct=self.notaria_pct,
            minuta_pct=self.minuta_pct,
            registro_pct=self.registro_pct,
            buffer_legales=self.buffer_legales,
            pct_consultoria=self.pct_consultoria,
        )

    def _build_proyecto(self) -> Proyecto:
        return Proyecto(
            nombre=self.nombre or "Sin nombre",
            localizacion=self.localizacion,
            ccaa=self.ccaa,
            descripcion=self.descripcion,
            equity=self.equity,
            acq_cost=self.acq_cost,
            tasacion=self.tasacion,
            hard_costs=self.hard_costs,
            soft_costs_sin_fee=self.soft_costs_sin_fee,
            comercial_cost=self.comercial_cost,
            ingresos_esperados=self.ingresos_esperados,
            total_unidades=self.total_unidades,
            meses_totales=self.meses_totales,
            capital_solicitado=self.capital_solicitado,
            primera_disposicion_solicitada=self.primera_disposicion_solicitada,
        )

    def calcular(self):
        """Lanza el analisis financiero (sin IA)."""
        try:
            proyecto = self._build_proyecto()
            params = self._build_params()
            r: ResultadoCompleto = analizar_proyecto(proyecto, params)
            self.resultado = r.model_dump(mode="json")
            self.error = ""
        except Exception as e:  # noqa: BLE001
            self.error = str(e)
            self.resultado = None

    async def analizar_con_ia(self):
        """Ejecuta el calculo financiero + analisis Claude + scoring."""
        # Import perezoso: evita que la app explote si falta ANTHROPIC_API_KEY
        # hasta que el usuario pulse el boton.
        from credere.ai import analizar_mercado, calcular_scoring

        try:
            proyecto = self._build_proyecto()
            params = self._build_params()
            r = analizar_proyecto(proyecto, params)
            analisis = analizar_mercado(r)
            scoring = calcular_scoring(r, analisis)
            self.resultado = {
                **r.model_dump(mode="json"),
                "analisis_mercado": analisis.model_dump(),
                "scoring": scoring,
            }
            self.error = ""
        except Exception as e:  # noqa: BLE001
            self.error = f"Error en analisis IA: {e}"

    def guardar(self):
        """Persiste proyecto + resultado en Supabase."""
        # Import perezoso: la app funciona sin Supabase hasta que guardes.
        from credere.db import get_supabase_client

        try:
            client = get_supabase_client()
            proyecto = self._build_proyecto()
            payload = proyecto.model_dump(mode="json")
            row = {
                "nombre": proyecto.nombre,
                "localizacion": proyecto.localizacion,
                "ccaa": proyecto.ccaa,
                "descripcion": proyecto.descripcion,
                "fecha_creacion": str(proyecto.fecha_creacion),
                "fecha_financiacion": (
                    str(proyecto.fecha_financiacion) if proyecto.fecha_financiacion else None
                ),
                "payload": payload,
            }
            inserted = client.table("proyectos").insert(row).execute()
            proyecto_id = inserted.data[0]["id"]

            if self.resultado:
                client.table("resultados").insert(
                    {
                        "proyecto_id": proyecto_id,
                        "params_snapshot": self.resultado["params"],
                        "prestamo": self.resultado["prestamo"],
                        "cashflow": self.resultado["cashflow"],
                        "ratios": self.resultado["ratios"],
                        "analisis_mercado": self.resultado.get("analisis_mercado"),
                        "scoring": self.resultado.get("scoring"),
                    }
                ).execute()
            self.error = ""
        except Exception as e:  # noqa: BLE001
            self.error = f"Error guardando: {e}"

    def cargar_proyectos(self):
        """Recarga la lista de proyectos desde Supabase."""
        from credere.db import get_supabase_client

        try:
            client = get_supabase_client()
            data = (
                client.table("proyectos")
                .select("id, nombre, localizacion, ccaa, fecha_creacion, created_at")
                .order("created_at", desc=True)
                .limit(100)
                .execute()
            )
            self.proyectos = data.data or []
            self.error = ""
        except Exception as e:  # noqa: BLE001
            self.error = f"Error cargando proyectos: {e}"
            self.proyectos = []
