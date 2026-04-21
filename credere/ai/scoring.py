"""Scoring final: combina el veredicto de Claude con senales cuantitativas del modelo.

No dependemos 100% del LLM: mezclamos su scoring con penalizaciones duras
por ratios financieros (p.ej. LTV > 80%, ROI promotor negativo) para que una
alucinacion del modelo no nos pase una operacion mala.
"""

from credere.ai.market_analysis import AnalisisMercado
from credere.calcs.inputs import ResultadoCompleto


def calcular_scoring(
    resultado: ResultadoCompleto,
    analisis: AnalisisMercado,
    peso_llm: float = 0.6,
    peso_cuantitativo: float = 0.4,
) -> dict:
    """
    Scoring compuesto 0-100.

    Penalizaciones duras (techo del scoring cuantitativo):
    - LTV > 80% -> techo 60
    - ROI promotor < 0 -> techo 40
    - Margen EBIT < 5% -> techo 50
    - LTC > 90% -> techo 55
    """
    ra = resultado.ratios

    # --- Score cuantitativo (0-100) --------------------------------------
    score_q = 100.0
    razones = []

    if ra.LTV > 0.80:
        score_q = min(score_q, 60)
        razones.append(f"LTV alto ({ra.LTV:.1%})")
    elif ra.LTV > 0.70:
        score_q -= 10
        razones.append(f"LTV elevado ({ra.LTV:.1%})")

    if ra.ROI_promotor < 0:
        score_q = min(score_q, 40)
        razones.append("ROI promotor negativo")
    elif ra.ROI_promotor_anualizado < 0.08:
        score_q -= 15
        razones.append(f"ROI promotor anualizado bajo ({ra.ROI_promotor_anualizado:.1%})")

    if ra.margen_ebit < 0.05:
        score_q = min(score_q, 50)
        razones.append(f"Margen EBIT bajo ({ra.margen_ebit:.1%})")

    if ra.LTC > 0.90:
        score_q = min(score_q, 55)
        razones.append(f"LTC alto ({ra.LTC:.1%})")

    score_q = max(0, min(100, score_q))

    # --- Composicion final -----------------------------------------------
    score_final = peso_llm * analisis.scoring + peso_cuantitativo * score_q

    if score_final >= 75:
        recomendacion = "aprobar"
    elif score_final >= 55:
        recomendacion = "aprobar_con_condiciones"
    elif score_final >= 35:
        recomendacion = "dudosa"
    else:
        recomendacion = "rechazar"

    return {
        "score_final": round(score_final, 1),
        "score_llm": analisis.scoring,
        "score_cuantitativo": round(score_q, 1),
        "recomendacion": recomendacion,
        "veredicto_llm": analisis.veredicto,
        "razones_cuantitativas": razones,
        "razonamiento_llm": analisis.razonamiento,
    }
