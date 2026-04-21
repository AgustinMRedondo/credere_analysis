# Credere Analysis

Herramienta interna de Credere Lending Capital para analizar operaciones inmobiliarias: cálculo determinista de préstamo, costes legales, disposiciones e intereses, más scoring de mercado asistido por IA.

## Stack

- **Reflex** (Python) — frontend + backend en un único repo
- **Supabase (Postgres)** — persistencia de proyectos y parámetros globales
- **Claude API** (`claude-opus-4-7`) con web search — análisis de mercado y scoring
- **reportlab** — generación de informes PDF

## Estructura prevista

```
credere/
  app.py                # Reflex entrypoint
  calcs/                # Lógica financiera pura (testeable)
    inputs.py           # Schemas Pydantic
    loan.py             # Préstamo total, primera disposición, costes legales
    cashflow.py         # Disposiciones, intereses, deuda mensual
    ratios.py           # LTV, LTC, ROI, EBIT
  ai/
    market_analysis.py  # Claude + web_search
    scoring.py          # Scoring macro + comparables
  db/
    client.py           # Supabase
    models.py
    migrations/
  reports/
    pdf.py
  tests/
    test_calcs.py       # Regresión con proyectos históricos
  pages/                # Reflex pages
  assets/
```

## Parámetros globales (todos editables desde UI)

**Deuda**
- Tasa anual: 13,5%
- Comisión apertura: 3%
- Comisión apertura a terceros: 1,5%

**Credere fee (legacy, revisar)**
- Comisión levantamiento: 1,5% sobre deuda total
- Fee sobre hard costs: 1,2%
- Fee sobre deuda: 0,3%

**Costes legales (nuevo)**
- IAJD: 1,5% (varía por CCAA)
- Notaría: 0,5%
- Minuta legal: 0,8%
- Registro propiedad: 0,2%
- Buffer Credere: 20% (aplica a notaría, minuta y registro; IAJD va al valor real)

**Consultoría**
- Consultoría: 2,8% sobre préstamo total
- Consultoría inicial: `consultoría × 3 / meses`

## Inputs por operación

- Metadata: nombre, localización, CCAA, descripción, fechas
- Financieros: equity, coste activo, tasación, hard costs, soft costs, coste comercial, ingresos esperados, unidades, meses
- Préstamo: capital solicitado, primera disposición solicitada
- Overrides opcionales de cualquier parámetro global

## Disclaimer

Propiedad intelectual y comercial de Credere Lending SL. Este documento y la herramienta no constituyen oferta de financiación.
