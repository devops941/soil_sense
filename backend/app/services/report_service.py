"""PDF Report Generation Service for SoilSense.

Generates professional agronomic reports in PDF format using ReportLab:
1. Individual Soil Sample Health Card Report
2. Complete Dataset & Regional Fertility Analysis Report
Strictly scoped to Madurai District, Tamil Nadu.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.parameter import ParameterDefinition
from app.models.sample import SoilParameterValue, SoilSample
from app.services import dashboard_service


# ---------------------------------------------------------------------------
# Brand Palette (Professional Agricultural Blue & White)
# ---------------------------------------------------------------------------
PRIMARY_BLUE = colors.HexColor("#1e40af")     # Deep Agri Blue
SECONDARY_BLUE = colors.HexColor("#3b82f6")   # Light Vibrant Blue
ACCENT_GREEN = colors.HexColor("#15803d")     # Deep Crop Green
BG_LIGHT = colors.HexColor("#f8fafc")         # Soft background
TEXT_DARK = colors.HexColor("#0f172a")        # Slate text
BORDER_COLOR = colors.HexColor("#cbd5e1")     # Subtle border
WARNING_AMBER = colors.HexColor("#d97706")    # Demo warning amber


def _build_styles() -> Dict[str, ParagraphStyle]:
    sample_styles = getSampleStyleSheet()
    styles: Dict[str, ParagraphStyle] = {}

    styles["ReportTitle"] = ParagraphStyle(
        "ReportTitle",
        parent=sample_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY_BLUE,
    )

    styles["ReportSubtitle"] = ParagraphStyle(
        "ReportSubtitle",
        parent=sample_styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=TEXT_DARK,
    )

    styles["SectionHeader"] = ParagraphStyle(
        "SectionHeader",
        parent=sample_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY_BLUE,
        spaceAfter=4,
    )

    styles["BodyTextCustom"] = ParagraphStyle(
        "BodyTextCustom",
        parent=sample_styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
    )

    styles["BodyBold"] = ParagraphStyle(
        "BodyBold",
        parent=sample_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=TEXT_DARK,
    )

    styles["Disclaimer"] = ParagraphStyle(
        "Disclaimer",
        parent=sample_styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748b"),
    )

    styles["BadgeDemo"] = ParagraphStyle(
        "BadgeDemo",
        parent=sample_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=WARNING_AMBER,
    )

    styles["BadgeVerified"] = ParagraphStyle(
        "BadgeVerified",
        parent=sample_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=ACCENT_GREEN,
    )

    styles["TableHeader"] = ParagraphStyle(
        "TableHeader",
        parent=sample_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.white,
    )

    styles["TableCell"] = ParagraphStyle(
        "TableCell",
        parent=sample_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=TEXT_DARK,
    )

    styles["TableCellBold"] = ParagraphStyle(
        "TableCellBold",
        parent=sample_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=TEXT_DARK,
    )

    return styles


def _get_agronomic_advisory(param_code: str, class_label: Optional[str]) -> str:
    """Provide scientifically-grounded advisory based on TNAU Agritech guidelines."""
    lbl = (class_label or "").lower()
    if param_code == "ph":
        if "acidic" in lbl:
            return "Soil is acidic. Apply agricultural lime (CaCO3) or dolomite based on buffer pH test to restore neutrality (6.5-7.5)."
        elif "alkaline" in lbl:
            return "Soil is alkaline. Apply agricultural gypsum (CaSO4·2H2O), green manure (Daincha/Sunnhemp), or farmyard manure (FYM) to improve permeability."
        else:
            return "Soil pH is in the optimal neutral range (6.5-7.3). Excellent nutrient availability; maintain organic matter levels."

    elif param_code == "nitrogen":
        if lbl == "low":
            return "Available N is Low (<240 kg/ha). Boost basal application of FYM (12.5 t/ha) and apply 25% extra nitrogenous fertilizer (Urea/Neem-coated urea) in split doses."
        elif lbl == "medium":
            return "Available N is Medium (240-480 kg/ha). Apply 100% of the recommended dose of nitrogen (RDN) for the designated crop according to TNAU schedule."
        else:
            return "Available N is High (>480 kg/ha). Reduce chemical N fertilizer application by 25% to prevent vegetative overgrowth and lodging."

    elif param_code == "phosphorus":
        if lbl == "low":
            return "Available P is Low (<11 kg/ha). Apply 25% extra phosphatic fertilizer (Single Super Phosphate / DAP) as basal dose. Inoculate with Phosphobacteria / VAM."
        elif lbl == "medium":
            return "Available P is Medium (11-22 kg/ha). Apply standard recommended dose of P (RDP) at sowing/planting."
        else:
            return "Available P is High (>22 kg/ha). Reduce chemical P fertilizer by 25-50% to prevent nutrient fixation and zinc deficiency."

    elif param_code == "potassium":
        if lbl == "low":
            return "Available K is Low (<110 kg/ha). Apply Muriate of Potash (MOP) in 2-3 split applications along with N to support root growth and stress tolerance."
        elif lbl == "medium":
            return "Available K is Medium (110-280 kg/ha). Apply recommended dose of potash (RDK) for crop maintenance."
        else:
            return "Available K is High (>280 kg/ha). Reduce chemical K fertilizer by 25%; common in semi-arid and clayey soils of Madurai."

    return "Maintain balanced fertilization according to TNAU crop production guidelines."


def generate_sample_pdf(db: Session, sample: SoilSample) -> bytes:
    """Generate a high-quality PDF Soil Health Card report for an individual soil sample."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = _build_styles()
    story = []

    # 1. Header Banner
    header_table = Table(
        [
            [
                Paragraph("<b>SoilSense</b> — Soil Health Intelligence", styles["ReportTitle"]),
                Paragraph("<b>Scope: Madurai District, TN</b><br/>Govt. Standard: " + settings.ACTIVE_STANDARD, styles["ReportSubtitle"]),
            ]
        ],
        colWidths=[350, 170],
    )
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_BLUE, spaceBefore=2, spaceAfter=8))

    # 2. Disclaimer & Data Integrity Badge
    data_source_badge = (
        "<b>DATA STATUS: VERIFIED LABORATORY RECORD</b>"
        if sample.data_source == "verified"
        else "<b>DATA STATUS: FIELD SURVEY ASSESSMENT RECORD</b>"
    )
    badge_style = styles["BadgeVerified"] if sample.data_source == "verified" else styles["BadgeDemo"]

    notice_table = Table(
        [
            [
                Paragraph(data_source_badge, badge_style),
                Paragraph(
                    "Advisory only. Conforms to TNAU Soil Rating Chart & ICAR Guidelines.",
                    styles["Disclaimer"],
                ),
            ]
        ],
        colWidths=[310, 210],
    )
    notice_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ])
    )
    story.append(notice_table)
    story.append(Spacer(1, 10))

    # 3. Sample Metadata Box
    loc_name = sample.location.name if sample.location else "N/A"
    district = (sample.location.district if sample.location else "Madurai") or "Madurai"
    taluk_block = (sample.location.taluk_block if sample.location else None) or loc_name
    village = (sample.location.village if sample.location else None) or loc_name

    meta_data = [
        [
            Paragraph("<b>Sample Code:</b>", styles["TableCellBold"]),
            Paragraph(sample.sample_code, styles["TableCell"]),
            Paragraph("<b>Sample Date:</b>", styles["TableCellBold"]),
            Paragraph(sample.sample_date.isoformat() if sample.sample_date else "N/A", styles["TableCell"]),
        ],
        [
            Paragraph("<b>District:</b>", styles["TableCellBold"]),
            Paragraph(f"{district} (Tamil Nadu)", styles["TableCellBold"]),
            Paragraph("<b>Taluk / Block:</b>", styles["TableCellBold"]),
            Paragraph(taluk_block, styles["TableCell"]),
        ],
        [
            Paragraph("<b>Village / Location:</b>", styles["TableCellBold"]),
            Paragraph(village, styles["TableCell"]),
            Paragraph("<b>Sampling Depth:</b>", styles["TableCellBold"]),
            Paragraph(f"{sample.depth_cm} cm" if sample.depth_cm else "0-20 cm", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Land Use / Crop:</b>", styles["TableCellBold"]),
            Paragraph(sample.land_use or "Agricultural", styles["TableCell"]),
            Paragraph("<b>Collector:</b>", styles["TableCellBold"]),
            Paragraph(sample.collector_name or "Department Officer / Field Agent", styles["TableCell"]),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[100, 160, 100, 160])
    meta_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(Paragraph("<b>Soil Sample Details</b>", styles["SectionHeader"]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 4. Overall Fertility Classification Banner
    cr = sample.classification_result
    fertility_label = cr.fertility_class if cr and cr.fertility_class else "Pending Evaluation"
    overall_status = cr.overall_status if cr and cr.overall_status else "Unclassified"

    fert_color = PRIMARY_BLUE
    if fertility_label == "High":
        fert_color = ACCENT_GREEN
    elif fertility_label == "Low":
        fert_color = colors.HexColor("#dc2626")

    fertility_banner = Table(
        [
            [
                Paragraph("<b>OVERALL SOIL FERTILITY:</b>", ParagraphStyle("FB", fontName="Helvetica-Bold", fontSize=12, textColor=colors.white)),
                Paragraph(f"<b>{fertility_label.upper()} FERTILITY</b>", ParagraphStyle("FL", fontName="Helvetica-Bold", fontSize=14, textColor=colors.white)),
                Paragraph(f"Status: {overall_status}", ParagraphStyle("FS", fontName="Helvetica", fontSize=9, textColor=colors.white)),
            ]
        ],
        colWidths=[180, 160, 180],
    )
    fertility_banner.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), fert_color),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(fertility_banner)
    story.append(Spacer(1, 12))

    # 5. Parameter Values & Classification Table
    param_def_map = {row.id: row for row in db.query(ParameterDefinition).all()}
    param_table_data = [
        [
            Paragraph("<b>Parameter</b>", styles["TableHeader"]),
            Paragraph("<b>Measured Value</b>", styles["TableHeader"]),
            Paragraph("<b>Unit</b>", styles["TableHeader"]),
            Paragraph("<b>Analytical Method</b>", styles["TableHeader"]),
            Paragraph("<b>TNAU Rating</b>", styles["TableHeader"]),
        ]
    ]

    # Map parameters
    code_to_pv = {}
    for pv in sample.parameter_values:
        pdef = param_def_map.get(pv.parameter_def_id)
        if pdef:
            code_to_pv[pdef.code] = pv

    param_display = [
        ("ph", "Soil Reaction (pH)", "pH", cr.ph_class if cr else "N/A"),
        ("nitrogen", "Available Nitrogen (N)", "kg/ha", cr.n_class if cr else "N/A"),
        ("phosphorus", "Available Phosphorus (P)", "kg/ha", cr.p_class if cr else "N/A"),
        ("potassium", "Available Potassium (K)", "kg/ha", cr.k_class if cr else "N/A"),
    ]

    for code, name, default_unit, rating in param_display:
        pv = code_to_pv.get(code)
        val_str = f"{pv.value:.2f}" if pv and code == "ph" else (f"{pv.value:.1f}" if pv else "Not Tested")
        unit_str = pv.unit if pv else default_unit
        method_str = pv.test_method if pv and pv.test_method else "Standard Method"
        rating_str = (rating or "Unclassified").replace("_", " ").title()

        param_table_data.append([
            Paragraph(name, styles["TableCellBold"]),
            Paragraph(val_str, styles["TableCell"]),
            Paragraph(unit_str, styles["TableCell"]),
            Paragraph(method_str, styles["TableCell"]),
            Paragraph(rating_str, styles["TableCellBold"]),
        ])

    ptable = Table(param_table_data, colWidths=[130, 80, 60, 160, 90])
    ptable.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(Paragraph("<b>Laboratory Nutrient Measurements & Ratings</b>", styles["SectionHeader"]))
    story.append(ptable)
    story.append(Spacer(1, 12))

    # 6. Agronomic Interpretation & Recommendations
    story.append(Paragraph("<b>Agricultural Advisory & Soil Management Recommendations</b>", styles["SectionHeader"]))
    advisory_rows = []
    for code, name, _, rating in param_display:
        adv_text = _get_agronomic_advisory(code, rating)
        advisory_rows.append([
            Paragraph(f"<b>{name}:</b>", styles["TableCellBold"]),
            Paragraph(adv_text, styles["TableCell"]),
        ])

    adv_table = Table(advisory_rows, colWidths=[140, 380])
    adv_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(adv_table)
    story.append(Spacer(1, 12))

    # 7. Scientific Sources & Footnote
    story.append(
        Paragraph(
            "<b>Scientific References:</b> Tamil Nadu Agricultural University (TNAU) Agritech Soil Rating Chart; "
            "ICAR Soil Health Card Scheme; IARI Soil Survey Manual (1970); Rammoorthy & Bajaj (1969) Fertilizer News 14(8):24-26.<br/>"
            "<b>Madurai KVK Contact:</b> Krishi Vigyan Kendra, Agricultural College & Research Institute, Madurai 625104.",
            styles["Disclaimer"],
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            f"Generated by SoilSense Soil Nutrient Intelligence System on {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}.",
            styles["Disclaimer"],
        )
    )

    doc.build(story)
    return buf.getvalue()


def generate_dataset_pdf(
    db: Session,
    data_source: Optional[str] = None,
    location_id: Optional[int] = None,
) -> bytes:
    """Generate a comprehensive regional soil analytics PDF report for Madurai District."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = _build_styles()
    story = []

    # 1. Header
    header_table = Table(
        [
            [
                Paragraph("<b>SoilSense</b> — District Soil Fertility Report", styles["ReportTitle"]),
                Paragraph("<b>Madurai District, Tamil Nadu</b><br/>Regional Nutrient Assessment", styles["ReportSubtitle"]),
            ]
        ],
        colWidths=[330, 190],
    )
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ])
    )
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY_BLUE, spaceBefore=2, spaceAfter=8))

    # Compute summary
    sdata = dashboard_service.summary(db, data_source=data_source, location_id=location_id)

    # 2. Executive KPI Summary Box
    tot = sdata["total_samples"]
    high = sdata["high_fertility_count"]
    med = sdata["medium_fertility_count"]
    low = sdata["low_fertility_count"]

    pct_high = f"{(high / tot * 100):.1f}%" if tot > 0 else "0%"
    pct_med = f"{(med / tot * 100):.1f}%" if tot > 0 else "0%"
    pct_low = f"{(low / tot * 100):.1f}%" if tot > 0 else "0%"

    kpi_table = Table(
        [
            [
                Paragraph("<b>Total Samples</b>", styles["TableHeader"]),
                Paragraph("<b>High Fertility</b>", styles["TableHeader"]),
                Paragraph("<b>Medium Fertility</b>", styles["TableHeader"]),
                Paragraph("<b>Low Fertility</b>", styles["TableHeader"]),
            ],
            [
                Paragraph(f"<font size=12><b>{tot}</b></font>", styles["TableCellBold"]),
                Paragraph(f"<font size=12 color='#15803d'><b>{high}</b></font> ({pct_high})", styles["TableCell"]),
                Paragraph(f"<font size=12 color='#1e40af'><b>{med}</b></font> ({pct_med})", styles["TableCell"]),
                Paragraph(f"<font size=12 color='#dc2626'><b>{low}</b></font> ({pct_low})", styles["TableCell"]),
            ],
        ],
        colWidths=[130, 130, 130, 130],
    )
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_BLUE),
            ("BACKGROUND", (0, 1), (-1, 1), BG_LIGHT),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(Paragraph("<b>Regional Soil Fertility Summary (KPIs)</b>", styles["SectionHeader"]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # 3. Nutrient Indices (Rammoorthy & Bajaj 1969)
    ni_table_data = [
        [
            Paragraph("<b>Nutrient</b>", styles["TableHeader"]),
            Paragraph("<b>Nutrient Index (NI)</b>", styles["TableHeader"]),
            Paragraph("<b>Classification Category</b>", styles["TableHeader"]),
            Paragraph("<b>Interpretation Benchmark</b>", styles["TableHeader"]),
        ]
    ]
    benchmarks = {
        "nitrogen": "Alkaline KMnO4 test (<1.67 Low | 1.67-2.33 Medium | >2.33 High)",
        "phosphorus": "Olsen NaHCO3 test (<1.67 Low | 1.67-2.33 Medium | >2.33 High)",
        "potassium": "Ammonium Acetate test (<1.67 Low | 1.67-2.33 Medium | >2.33 High)",
    }

    for ni in sdata.get("nutrient_indices", []):
        param_name = ni["parameter_code"].title()
        val = ni["index_value"]
        cls_lbl = ni["class_label"]
        bm = benchmarks.get(ni["parameter_code"], "<1.67 Low | 1.67-2.33 Medium | >2.33 High")

        ni_table_data.append([
            Paragraph(f"Available {param_name}", styles["TableCellBold"]),
            Paragraph(f"<b>{val:.3f}</b>", styles["TableCell"]),
            Paragraph(f"<b>{cls_lbl}</b>", styles["TableCellBold"]),
            Paragraph(bm, styles["TableCell"]),
        ])

    ni_table = Table(ni_table_data, colWidths=[120, 110, 110, 180])
    ni_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), SECONDARY_BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(Paragraph("<b>Macronutrient Indices (Rammoorthy & Bajaj Standard)</b>", styles["SectionHeader"]))
    story.append(ni_table)
    story.append(Spacer(1, 12))

    # 4. Location-Wise Comparison Table
    loc_table_data = [
        [
            Paragraph("<b>Location / Block</b>", styles["TableHeader"]),
            Paragraph("<b>Samples</b>", styles["TableHeader"]),
            Paragraph("<b>Avg pH</b>", styles["TableHeader"]),
            Paragraph("<b>Avg N (kg/ha)</b>", styles["TableHeader"]),
            Paragraph("<b>Avg P (kg/ha)</b>", styles["TableHeader"]),
            Paragraph("<b>Avg K (kg/ha)</b>", styles["TableHeader"]),
            Paragraph("<b>Dominant Class</b>", styles["TableHeader"]),
        ]
    ]

    for loc in sdata.get("location_wise_stats", [])[:15]:
        loc_name = loc["location_name"]
        sc = str(loc["sample_count"])
        aph = f"{loc['avg_ph']:.2f}" if loc["avg_ph"] is not None else "-"
        an = f"{loc['avg_nitrogen']:.1f}" if loc["avg_nitrogen"] is not None else "-"
        ap = f"{loc['avg_phosphorus']:.1f}" if loc["avg_phosphorus"] is not None else "-"
        ak = f"{loc['avg_potassium']:.1f}" if loc["avg_potassium"] is not None else "-"
        df = loc["dominant_fertility"]

        loc_table_data.append([
            Paragraph(loc_name, styles["TableCellBold"]),
            Paragraph(sc, styles["TableCell"]),
            Paragraph(aph, styles["TableCell"]),
            Paragraph(an, styles["TableCell"]),
            Paragraph(ap, styles["TableCell"]),
            Paragraph(ak, styles["TableCell"]),
            Paragraph(df, styles["TableCell"]),
        ])

    loc_table = Table(loc_table_data, colWidths=[130, 50, 55, 75, 75, 75, 60])
    loc_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_BLUE),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ("PADDING", (0, 0), (-1, -1), 4.5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )
    story.append(Paragraph("<b>Block & Location Nutrient Profiles</b>", styles["SectionHeader"]))
    story.append(loc_table)
    story.append(Spacer(1, 12))

    # 5. Agronomic Recommendations for Madurai District
    story.append(Paragraph("<b>Regional Agronomic Recommendations (Madurai District)</b>", styles["SectionHeader"]))
    regional_notes = (
        "1. <b>Nitrogen Management:</b> Most Madurai soils exhibit Low-to-Medium nitrogen reserves due to low organic "
        "matter in high temperature semi-arid climate. Promote green manuring with Daincha (Sesbania aculeata) before paddy.<br/>"
        "2. <b>Phosphorus Efficiency:</b> Calcareous soils in Thirumangalam, Usilampatti, and Vadipatti fix soluble phosphorus. "
        "Apply phosphobacteria biofertilizer along with farmyard manure to increase P mobilization.<br/>"
        "3. <b>Potassium Reserves:</b> Black and mixed alluvial soils generally have medium-to-high potassium. Adjust potash "
        "doses based on specific crop requirements.<br/>"
        "4. <b>Data Policy:</b> All analyses conform strictly to Madurai District agricultural boundaries under verified field sampling protocols."
    )
    story.append(
        Table(
            [[Paragraph(regional_notes, styles["TableCell"])]],
            colWidths=[520],
        )
    )
    story.append(Spacer(1, 10))

    # 6. Footer & Citations
    story.append(
        Paragraph(
            "<b>Authorities:</b> Tamil Nadu Agricultural University (TNAU) Agritech Portal | ICAR Soil Health Card Portal | "
            "District Agricultural Department, Madurai.<br/>"
            f"Generated by SoilSense Analytical Engine on {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}.",
            styles["Disclaimer"],
        )
    )

    doc.build(story)
    return buf.getvalue()
