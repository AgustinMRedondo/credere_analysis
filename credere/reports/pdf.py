"""Generacion de informe PDF del analisis.

Placeholder minimo: portada + condiciones de deuda + resumen ratios + cashflow.
Tomar de referencia `modelo_basico.py` v1 (funcion `generar_pdf`) para los bloques
adicionales (graficos matplotlib, tabla de disposiciones apaisada).
"""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image as RLImage,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from credere.calcs.inputs import ResultadoCompleto

ASSETS = Path(__file__).resolve().parent.parent.parent / "assets"
AZUL = colors.HexColor("#003D6E")
CELESTE = colors.HexColor("#E6F4F1")


def _estilos():
    base = getSampleStyleSheet()
    return {
        "normal": base["Normal"],
        "titulo": ParagraphStyle(
            name="Titulo", alignment=TA_CENTER, fontSize=18, textColor=AZUL, spaceAfter=12
        ),
        "seccion": ParagraphStyle(
            name="Seccion", alignment=TA_CENTER, fontSize=14, textColor=AZUL, spaceAfter=10
        ),
    }


def _tabla(data: list[list[str]]) -> Table:
    t = Table(data, colWidths=[220, 180])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), CELESTE),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return t


def generar_informe_pdf(resultado: ResultadoCompleto, out_path: str | Path | None = None) -> Path:
    """Genera el PDF y devuelve la ruta absoluta."""
    s = _estilos()
    p = resultado.proyecto
    pr = resultado.prestamo
    ra = resultado.ratios

    nombre = p.nombre.replace(" ", "_")
    out = Path(out_path) if out_path else Path(f"informe_credere_{nombre}_{p.fecha_creacion}.pdf")
    doc = SimpleDocTemplate(str(out), pagesize=A4)

    story = []
    logo = ASSETS / "Isotipo_Credere1.png"
    if logo.exists():
        story.append(RLImage(str(logo), width=60, height=60))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Informe Credere Lending", s["titulo"]))
    story.append(Paragraph(f"<b>Proyecto:</b> {p.nombre}", s["seccion"]))
    story.append(Paragraph(f"<b>Localizacion:</b> {p.localizacion} ({p.ccaa})", s["normal"]))
    story.append(Paragraph(f"<b>Descripcion:</b> {p.descripcion}", s["normal"]))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Condiciones de deuda", s["seccion"]))
    story.append(
        _tabla(
            [
                ["Concepto", "Valor"],
                ["Tasa anual", f"{resultado.params.tasa_anual_deuda:.2%}"],
                ["Comision apertura", f"{resultado.params.comision_apertura:.2%}"],
                ["Duracion", f"{p.meses_totales} meses"],
                ["IAJD (CCAA)", f"{resultado.params.iajd_pct:.2%}"],
            ]
        )
    )
    story.append(Spacer(1, 16))

    story.append(Paragraph("Prestamo", s["seccion"]))
    story.append(
        _tabla(
            [
                ["Concepto", "Importe"],
                ["Capital solicitado", f"{pr.capital_solicitado:,.0f} EUR"],
                ["IAJD", f"{pr.costes_legales.iajd:,.0f} EUR"],
                ["Notaria", f"{pr.costes_legales.notaria:,.0f} EUR"],
                ["Minuta legal", f"{pr.costes_legales.minuta:,.0f} EUR"],
                ["Registro propiedad", f"{pr.costes_legales.registro:,.0f} EUR"],
                ["Costes legales (total)", f"{pr.costes_legales.total:,.0f} EUR"],
                ["Credere fee", f"{pr.deuda_iterativa.credere_fee:,.0f} EUR"],
                ["Consultoria", f"{pr.consultoria:,.0f} EUR"],
                ["Prestamo total", f"{pr.prestamo_total:,.0f} EUR"],
                ["Primera disposicion total", f"{pr.primera_disposicion_total:,.0f} EUR"],
            ]
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("Ratios", s["seccion"]))
    story.append(
        _tabla(
            [
                ["Concepto", "Valor"],
                ["EBITDA", f"{ra.EBITDA:,.0f} EUR"],
                ["EBIT", f"{ra.EBIT:,.0f} EUR"],
                ["Margen EBIT", f"{ra.margen_ebit:.2%}"],
                ["LTV", f"{ra.LTV:.2%}"],
                ["LTV inicial", f"{ra.LTV_inicial:.2%}"],
                ["LTC", f"{ra.LTC:.2%}"],
                ["ROI promotor anual.", f"{ra.ROI_promotor_anualizado:.2%}"],
                ["ROI inversor anual.", f"{ra.ROI_inversor_anualizado:.2%}"],
                ["Coste real deuda", f"{ra.coste_real_deuda:.2%}"],
            ]
        )
    )

    doc.build(story)
    return out.resolve()
