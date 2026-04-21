"""Analisis de mercado via Claude API con web search nativa.

Pide a Claude que busque en internet comparables, datos macroeconomicos
(Euribor, evolucion precio/m2, paro, inmigracion) y publique un veredicto
estructurado sobre si la operacion que le pasamos es atractiva.

Requiere ANTHROPIC_API_KEY en entorno.
"""

from __future__ import annotations

import json
import os
from typing import Any

import anthropic
from pydantic import BaseModel

from credere.calcs.inputs import ResultadoCompleto

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")


class AnalisisMercado(BaseModel):
    """Output estructurado del analisis de mercado."""

    scoring: int  # 0-100
    veredicto: str  # "atractiva" | "dudosa" | "rechazar"
    razonamiento: str
    riesgos: list[str]
    oportunidades: list[str]
    comparables: list[dict[str, Any]]
    indicadores_macro: dict[str, Any]
    fuentes: list[str]


SYSTEM_PROMPT = """Eres un analista senior de riesgo inmobiliario de Credere Lending Capital.
Analizas operaciones de prestamo puente / promotor sobre activos residenciales, locales
y suelo en Espana.

Tu objetivo: dada la ficha de una operacion, emitir un veredicto estructurado.

Debes usar la herramienta web_search para buscar:
1. Precio por m2 actual en la zona (idealista, fotocasa, eleconomista).
2. Evolucion del Euribor y tipos hipotecarios en los ultimos 6 meses.
3. Datos macro relevantes (paro provincial, inflacion, stock de vivienda).
4. Comparables recientes (ventas o promociones similares en la misma zona).
5. Cualquier noticia regulatoria (IAJD por CCAA, bonificaciones, cambios urbanisticos).

Devuelve SIEMPRE un unico objeto JSON con esta forma exacta (sin texto alrededor):

{
  "scoring": <entero 0-100>,
  "veredicto": "<atractiva|dudosa|rechazar>",
  "razonamiento": "<3-5 parrafos>",
  "riesgos": ["<riesgo 1>", ...],
  "oportunidades": ["<oportunidad 1>", ...],
  "comparables": [{"direccion": "...", "precio_m2": 0, "fuente": "..."}, ...],
  "indicadores_macro": {"euribor_12m": 0.0, "paro_provincia": 0.0, ...},
  "fuentes": ["<url1>", ...]
}

Criterios de scoring orientativos:
- 80-100: operacion solida, LTV < 60%, EBIT > 15% ingresos, zona con demanda creciente.
- 60-79: viable con algun riesgo acotado.
- 40-59: dudosa, pedir garantias adicionales.
- 0-39: rechazar."""


def _ficha_proyecto(r: ResultadoCompleto) -> str:
    p = r.proyecto
    pr = r.prestamo
    ra = r.ratios
    return f"""
FICHA DE OPERACION
==================
Proyecto: {p.nombre}
Localizacion: {p.localizacion} ({p.ccaa})
Descripcion: {p.descripcion}
Duracion: {p.meses_totales} meses
Tipo de activo: {p.total_unidades} unidad(es)

ECONOMICOS
----------
Equity promotor:                {p.equity:,.0f} EUR
Coste adquisicion:              {p.acq_cost:,.0f} EUR
Valor tasacion:                 {p.tasacion:,.0f} EUR
Hard costs (CAPEX):             {p.hard_costs:,.0f} EUR
Soft costs:                     {p.soft_costs_sin_fee:,.0f} EUR
Coste comercial:                {p.comercial_cost:,.0f} EUR
Ingresos esperados:             {p.ingresos_esperados:,.0f} EUR
Precio por unidad:              {ra.precio_unidad:,.0f} EUR

PRESTAMO
--------
Capital solicitado:             {pr.capital_solicitado:,.0f} EUR
Costes legales (total):         {pr.costes_legales.total:,.0f} EUR
  IAJD:                         {pr.costes_legales.iajd:,.0f} EUR
  Notaria:                      {pr.costes_legales.notaria:,.0f} EUR
  Minuta legal:                 {pr.costes_legales.minuta:,.0f} EUR
  Registro propiedad:           {pr.costes_legales.registro:,.0f} EUR
Prestamo total:                 {pr.prestamo_total:,.0f} EUR
Primera disposicion total:      {pr.primera_disposicion_total:,.0f} EUR
Consultoria:                    {pr.consultoria:,.0f} EUR
Credere fee:                    {pr.deuda_iterativa.credere_fee:,.0f} EUR

RATIOS
------
EBITDA:                         {ra.EBITDA:,.0f} EUR
EBIT:                           {ra.EBIT:,.0f} EUR
Margen EBIT:                    {ra.margen_ebit:.2%}
LTV:                            {ra.LTV:.2%}
LTV inicial:                    {ra.LTV_inicial:.2%}
LTC:                            {ra.LTC:.2%}
ROI promotor (anualizado):      {ra.ROI_promotor_anualizado:.2%}
ROI inversor (anualizado):      {ra.ROI_inversor_anualizado:.2%}
Coste real deuda:               {ra.coste_real_deuda:.2%}

PARAMETROS APLICADOS
--------------------
Tipo interes anual:             {r.params.tasa_anual_deuda:.2%}
Comision apertura:              {r.params.comision_apertura:.2%}
IAJD (%):                       {r.params.iajd_pct:.2%}
Buffer legales (Credere):       {r.params.buffer_legales:.2%}
""".strip()


def analizar_mercado(
    resultado: ResultadoCompleto,
    model: str | None = None,
    max_tokens: int = 8192,
) -> AnalisisMercado:
    """Llama a Claude con web search y devuelve el analisis parseado."""
    client = anthropic.Anthropic()
    ficha = _ficha_proyecto(resultado)

    response = client.messages.create(
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 8,
            },
        ],
        messages=[{"role": "user", "content": ficha}],
    )

    texto = _extraer_json(response)
    data = json.loads(texto)
    return AnalisisMercado(**data)


def _extraer_json(response) -> str:
    """Extrae el JSON del ultimo bloque de texto de la respuesta de Claude."""
    for block in reversed(response.content):
        if getattr(block, "type", None) == "text":
            t = block.text.strip()
            # Tolera ```json ... ``` o json suelto
            if t.startswith("```"):
                t = t.split("```", 2)[1]
                if t.startswith("json"):
                    t = t[4:].strip()
            return t
    raise RuntimeError("Respuesta de Claude sin bloque de texto")
