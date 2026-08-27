"""
generate_test_reports.py
========================
Generates realistic synthetic drilling documents for testing:
  1. Digital Well Completion Report (WCR) for Volve 15/9-F-11B
  2. Digital Daily Drilling Report (DDR) for Volve 15/9-F-12
  3. Scanned/low-density legacy document with image-only content
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect


def generate_wcr_pdf(output_path: str):
    """Generates a realistic multi-page Digital Well Completion Report."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
    )
    h2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"),
    )
    body_style = styles["Normal"]

    # Page 1: Well Summary & Header Table
    story.append(Paragraph("WELL COMPLETION REPORT: WELL 15/9-F-11B", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("OPERATOR: STATOIL ASA | LICENCE: PL 046 | FIELD: VOLVE", body_style))
    story.append(Spacer(1, 14))

    table_data = [
        ["Well Name / UWI", "15/9-F-11B", "Country", "Norway"],
        ["Operator", "Statoil ASA", "Field Name", "Volve"],
        ["Spud Date", "2007-08-24", "Completion Date", "2007-10-15"],
        ["Surface Latitude", "58.4394 N", "Surface Longitude", "1.8875 E"],
        ["Total Depth (MD)", "3200.0 m", "Water Depth", "86.0 m"],
    ]
    t = Table(table_data, colWidths=[130, 130, 130, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    story.append(Paragraph("1. Executive Summary", h2_style))
    story.append(Paragraph(
        "Well 15/9-F-11B was drilled as a production well in the southern part of the Volve Field. "
        "The objective was to penetrate the Jurassic Hugin Formation sandstone reservoir. "
        "Total depth of 3200.0 m MD was reached successfully in the Skagerrak Formation.",
        body_style,
    ))

    # Page 2: Geological Summary
    story.append(PageBreak())
    story.append(Paragraph("2. Geological & Stratigraphic Summary", h2_style))
    story.append(Paragraph(
        "The well penetrated standard North Sea stratigraphy including Nordland, Hordaland, Rogaland, "
        "Chalk Group, and Viking Group before entering the target Hugin Formation at 2420 m MD. "
        "The Skagerrak Formation was penetrated at 2750 m MD to total depth at 3200 m MD.",
        body_style,
    ))
    story.append(Spacer(1, 10))
    geo_table_data = [
        ["Formation", "Top MD (m)", "Base MD (m)", "Lithology"],
        ["Hugin Formation", "2420.0", "2750.0", "Sandstone reservoir, fine to medium"],
        ["Skagerrak Formation", "2750.0", "3200.0", "Interbedded sandstone and shale"],
    ]
    geo_t = Table(geo_table_data, colWidths=[140, 90, 90, 200])
    geo_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(geo_t)

    # Page 3: Operational Incidents (Mud Loss) & Mud Program
    story.append(PageBreak())
    story.append(Paragraph("3. Operational Drilling Incidents & Mud Program", h2_style))
    story.append(Paragraph(
        "Mud Program: The 12-1/4 inch section from 2400.0 m to 2600.0 m MD was drilled using OBM "
        "with mud weight 1.45 SG. On 2007-09-12, while drilling through the Hugin Formation at 2450.0 m MD, "
        "partial mud losses of 15 bbl/hr were encountered. Pit level dropped steadily over 2 hours. "
        "Mitigation: Pumped LCM pill (50 bbl, 40 ppb LCM blend); losses reduced to seepage rate before drilling resumed.",
        body_style,
    ))

    # Page 4: Casing & Cementing Operations
    story.append(PageBreak())
    story.append(Paragraph("4. Casing & Cementing Operations", h2_style))
    story.append(Paragraph(
        "Surface casing 13-3/8 inch (68 ppf) was set at 1200 m MD. "
        "Intermediate casing 9-5/8 inch (47 ppf) was set at 2600.0 m MD and cemented without issues "
        "with 280 bbl Class G + silica cement, achieving top of cement at 1800 m MD.",
        body_style,
    ))
    story.append(Spacer(1, 10))
    casing_table_data = [
        ["Casing Type", "Shoe MD (m)", "Size (in)", "Weight (ppf)", "TOC (m)"],
        ["Surface", "1200.0", "13.375", "68.0", "Surface"],
        ["Intermediate", "2600.0", "9.625", "47.0", "1800.0"],
    ]
    casing_t = Table(casing_table_data, colWidths=[110, 100, 90, 100, 120])
    casing_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(casing_t)

    # Page 5: Stuck Pipe Incident
    story.append(PageBreak())
    story.append(Paragraph("5. Deep Section Operations & Lessons Learned", h2_style))
    story.append(Paragraph(
        "On 2007-09-20, at measured depth 2810.0 m MD in the Skagerrak Formation, the drillstring became mechanically stuck "
        "while tripping out through a tight hole section. Overpull of 40 klbs was observed and the crew was unable to rotate string. "
        "Action taken: Worked pipe free with jarring after 6 hours; wiper trip run before continuing.",
        body_style,
    ))

    doc.build(story)


def generate_ddr_pdf(output_path: str):
    """Generates a realistic Digital Daily Drilling Report for offset well 15/9-F-12."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D"),
    )
    body_style = styles["Normal"]

    story.append(Paragraph("DAILY DRILLING REPORT: WELL 15/9-F-12", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("OPERATOR: STATOIL ASA | FIELD: VOLVE | REPORT DATE: 2008-01-28", body_style))
    story.append(Spacer(1, 12))

    table_data = [
        ["Well ID", "15/9-F-12", "Spud Date", "2008-01-10"],
        ["Latitude", "58.4410 N", "Longitude", "1.8890 E"],
        ["Current Depth", "2510.0 m", "Target TD", "3350.0 m"],
    ]
    t = Table(table_data, colWidths=[120, 140, 120, 140])
    t.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(PageBreak())
    story.append(Paragraph("24-Hour Operations Summary & Significant Events", styles["Heading2"]))
    story.append(Paragraph(
        "Formation Tops: Entered Hugin Formation sandstone at 2410.0 m MD (gas bearing). "
        "Casing Program: 9-5/8 inch intermediate casing (47 ppf) previously set at 2480.0 m MD and cemented to 1750 m MD TOC with 250 bbl Class G cement. "
        "Mud Program: 8-1/2 inch hole section drilled using 1.50 SG OBM from 2480 m to current depth. "
        "On 2008-01-28 at 2510.0 m MD in the Hugin Formation, a gas kick was taken while drilling 8-1/2 inch hole section. "
        "Pit volume gain of 12 bbl observed with flow rate increase. "
        "Action taken: Shut in well on annular BOP; circulated out influx using Driller's Method.",
        body_style,
    ))

    doc.build(story)


def generate_scanned_pdf(output_path: str):
    """Generates an image-like zero-text density PDF simulating a scanned legacy paper log."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []

    # Pure graphic box simulating scanned bitmap with zero extractable text
    d = Drawing(400, 500)
    d.add(Rect(10, 10, 380, 480, fillColor=colors.HexColor("#CBD5E0"), strokeColor=colors.black))
    story.append(d)

    doc.build(story)


def generate_all_samples(base_dir: str = "data/sample_reports"):
    wcr_path = os.path.join(base_dir, "wcr_volve_15_9_f11b.pdf")
    ddr_path = os.path.join(base_dir, "ddr_volve_15_9_f12.pdf")
    scan_path = os.path.join(base_dir, "scanned_legacy_log_scan.pdf")

    generate_wcr_pdf(wcr_path)
    generate_ddr_pdf(ddr_path)
    generate_scanned_pdf(scan_path)
    print(f"Generated sample documents in {base_dir}")


if __name__ == "__main__":
    generate_all_samples()
