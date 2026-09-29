import os
import json
import random
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Fixed random seed for reproducibility
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PDFS_DIR = SYNTHETIC_DIR / "pdfs"
EVAL_DIR = DATA_DIR / "eval"

# Tenant Exporter details (Fictional only)
TENANTS = {
    "exp_a": {
        "name": "Indus Crest Textiles Ltd.",
        "ntn": "7182934-1",
        "address": "Plot 42, Export Processing Zone, Landhi, Karachi, Pakistan",
        "email": "export@induscrest-textiles.pk",
        "phone": "+92-21-35019841"
    },
    "exp_b": {
        "name": "Silver Loom Apparel Corp.",
        "ntn": "8291045-3",
        "address": "Sector 15, Korangi Industrial Area, Karachi, Pakistan",
        "email": "operations@silverloomapparel.pk",
        "phone": "+92-21-35028912"
    },
    "exp_c": {
        "name": "Karakoram Fabrics Pvt. Ltd.",
        "ntn": "9302156-5",
        "address": "Phase 2, SITE Industrial Area, Karachi, Pakistan",
        "email": "trade@karakoramfabrics.pk",
        "phone": "+92-21-35037823"
    }
}

# Buyers / Consignees (Fictional only)
BUYERS = [
    {
        "name": "Nordic Vogue Imports AB",
        "address": "Hamngatan 14, 411 17 Gothenburg, Sweden",
        "country": "Sweden",
        "port": "Gothenburg",
        "bank": "Nordic Merchant Bank AB, Stockholm",
        "bank_swift": "NMBSSEESS"
    },
    {
        "name": "Global Thread Retailers Inc.",
        "address": "840 Commerce Blvd, Suite 300, Dallas, TX 75201, USA",
        "country": "USA",
        "port": "Houston",
        "bank": "Apex Commerce Bank of Texas, Dallas",
        "bank_swift": "ACBTUS44"
    },
    {
        "name": "Bavaria Garment Distribution GmbH",
        "address": "Industriestrasse 28, 80339 Munich, Germany",
        "country": "Germany",
        "port": "Hamburg",
        "bank": "Bavaria Commercial Kreditbank AG, Munich",
        "bank_swift": "BCKBDE88"
    },
    {
        "name": "Meridian Clothiers Ltd.",
        "address": "52 Albert Square, Manchester M2 4JW, United Kingdom",
        "country": "United Kingdom",
        "port": "Liverpool",
        "bank": "Crown Union Mercantile Bank, London",
        "bank_swift": "CUMBGB22"
    }
]

# Product Definitions
PRODUCTS = {
    "cotton_tshirts": {
        "name": "cotton t-shirts",
        "description": "100% Combed Cotton Men's T-Shirts (Crew Neck, Assorted Sizes)",
        "hs_code": "6109.10",
        "unit": "PCS",
        "default_qty": 15000,
        "default_unit_price": 3.00,
        "package_type": "500 Cartons"
    },
    "terry_towels": {
        "name": "terry towels",
        "description": "100% Cotton Bleached Terry Bath & Hand Towels (500 GSM)",
        "hs_code": "6302.60",
        "unit": "KGS",
        "default_qty": 10000,
        "default_unit_price": 5.20,
        "package_type": "400 Bales"
    },
    "denim_trousers": {
        "name": "denim trousers",
        "description": "Men's Cotton Denim Trousers 5-Pocket Regular Fit (12.5 oz)",
        "hs_code": "6203.42",
        "unit": "PCS",
        "default_qty": 8000,
        "default_unit_price": 8.00,
        "package_type": "400 Cartons"
    }
}

# Specification of the 10 Shipments
SHIPMENTS_CONFIG = [
    {
        "shipment_id": "SHP-01",
        "tenant_id": "exp_a",
        "port": "Port Qasim",
        "po_number": "PO-9841",
        "container_id": "C-402",
        "lc_number": "LC-2291",
        "gd_number": "GD-5510",
        "product_key": "cotton_tshirts",
        "buyer_idx": 0,
        "vessel": "MV Indus Voyager",
        "voyage": "V-2601",
        "po_date": "2026-03-05",
        "lc_date": "2026-03-12",
        "lc_expiry": "2026-05-15",
        "bl_date": "2026-04-10",
        "gd_date": "2026-04-08",
        "hold_date": "2026-04-12",
        "po_amount": 45000.0,
        "lc_amount": 45000.0,
        "gd_declared_value": 48500.0,  # DISCREPANCY: GD declared value higher than LC
        "po_hs_code": "6109.10",
        "gd_hs_code": "6109.10",
        "bl_weight": 14200,
        "gd_weight": 14200,
        "lc_requires_inspection": False,
        "discrepancy": "GD declared value (USD 48,500) is higher than LC amount (USD 45,000)"
    },
    {
        "shipment_id": "SHP-02",
        "tenant_id": "exp_b",
        "port": "Karachi Port",
        "po_number": "PO-9842",
        "container_id": "C-403",
        "lc_number": "LC-2292",
        "gd_number": "GD-5511",
        "product_key": "terry_towels",
        "buyer_idx": 1,
        "vessel": "MV Arabian Wave",
        "voyage": "V-1104",
        "po_date": "2026-03-06",
        "lc_date": "2026-03-14",
        "lc_expiry": "2026-05-20",
        "bl_date": "2026-04-12",
        "gd_date": "2026-04-11",
        "hold_date": "2026-04-14",
        "po_amount": 52000.0,
        "lc_amount": 52000.0,
        "gd_declared_value": 52000.0,
        "po_hs_code": "6109.10",      # DISCREPANCY: PO has 6109.10, but GD has 6302.60
        "gd_hs_code": "6302.60",
        "bl_weight": 12500,
        "gd_weight": 12500,
        "lc_requires_inspection": False,
        "discrepancy": "HS code on PO differs from HS code on GD"
    },
    {
        "shipment_id": "SHP-03",
        "tenant_id": "exp_c",
        "port": "Port Qasim",
        "po_number": "PO-9843",
        "container_id": "C-404",
        "lc_number": "LC-2293",
        "gd_number": "GD-5512",
        "product_key": "denim_trousers",
        "buyer_idx": 2,
        "vessel": "MV Karakoram Pearl",
        "voyage": "V-3309",
        "po_date": "2026-03-08",
        "lc_date": "2026-03-15",
        "lc_expiry": "2026-04-10",    # DISCREPANCY: LC expiry is BEFORE BL date (2026-04-15)
        "bl_date": "2026-04-15",
        "gd_date": "2026-04-12",
        "hold_date": "2026-04-16",
        "po_amount": 64000.0,
        "lc_amount": 64000.0,
        "gd_declared_value": 64000.0,
        "po_hs_code": "6203.42",
        "gd_hs_code": "6203.42",
        "bl_weight": 9800,
        "gd_weight": 9800,
        "lc_requires_inspection": False,
        "discrepancy": "LC expiry date is before the Bill of Lading date"
    },
    {
        "shipment_id": "SHP-04",
        "tenant_id": "exp_a",
        "port": "Karachi Port",
        "po_number": "PO-9844",
        "container_id": "C-405",
        "lc_number": "LC-2294",
        "gd_number": "GD-5513",
        "product_key": "cotton_tshirts",
        "buyer_idx": 3,
        "vessel": "MV Sindh Star",
        "voyage": "V-5512",
        "po_date": "2026-03-10",
        "lc_date": "2026-03-18",
        "lc_expiry": "2026-05-25",
        "bl_date": "2026-04-18",
        "gd_date": "2026-04-16",
        "hold_date": "2026-04-20",
        "po_amount": 45000.0,
        "lc_amount": 45000.0,
        "gd_declared_value": 45000.0,
        "po_hs_code": "6109.10",
        "gd_hs_code": "6109.10",
        "bl_weight": 14200,
        "gd_weight": 14200,
        "lc_requires_inspection": True,  # DISCREPANCY: LC requires inspection cert, missing from docs
        "discrepancy": "LC requires an inspection certificate, but it is not among the shipment documents"
    },
    {
        "shipment_id": "SHP-05",
        "tenant_id": "exp_b",
        "port": "Port Qasim",
        "po_number": "PO-9845",
        "container_id": "C-406",
        "lc_number": "LC-2295",
        "gd_number": "GD-5514",
        "product_key": "terry_towels",
        "buyer_idx": 0,
        "vessel": "MV Orient Crest",
        "voyage": "V-0821",
        "po_date": "2026-03-12",
        "lc_date": "2026-03-20",
        "lc_expiry": "2026-05-30",
        "bl_date": "2026-04-20",
        "gd_date": "2026-04-18",
        "hold_date": "2026-04-22",
        "po_amount": 52000.0,
        "lc_amount": 52000.0,
        "gd_declared_value": 52000.0,
        "po_hs_code": "6302.60",
        "gd_hs_code": "6302.60",
        "bl_weight": 19850,              # DISCREPANCY: gross weight on BL differs from GD weight
        "gd_weight": 16400,
        "lc_requires_inspection": False,
        "discrepancy": "gross weight on BL differs from GD weight"
    },
    {
        "shipment_id": "SHP-06",
        "tenant_id": "exp_c",
        "port": "Karachi Port",
        "po_number": "PO-9846",
        "container_id": "C-407",
        "lc_number": "LC-2296",
        "gd_number": "GD-5515",
        "product_key": "denim_trousers",
        "buyer_idx": 1,
        "vessel": "MV Indus Voyager",
        "voyage": "V-2602",
        "po_date": "2026-03-14",
        "lc_date": "2026-03-22",
        "lc_expiry": "2026-05-30",
        "bl_date": "2026-04-22",
        "gd_date": "2026-04-20",
        "hold_date": "2026-04-24",
        "po_amount": 64000.0,
        "lc_amount": 64000.0,
        "gd_declared_value": 64000.0,
        "po_hs_code": "6203.42",
        "gd_hs_code": "6203.42",
        "bl_weight": 9800,
        "gd_weight": 9800,
        "lc_requires_inspection": False,
        "discrepancy": "none"
    },
    {
        "shipment_id": "SHP-07",
        "tenant_id": "exp_a",
        "port": "Port Qasim",
        "po_number": "PO-9847",
        "container_id": "C-408",
        "lc_number": "LC-2297",
        "gd_number": "GD-5516",
        "product_key": "cotton_tshirts",
        "buyer_idx": 2,
        "vessel": "MV Arabian Wave",
        "voyage": "V-1105",
        "po_date": "2026-03-15",
        "lc_date": "2026-03-24",
        "lc_expiry": "2026-06-05",
        "bl_date": "2026-04-25",
        "gd_date": "2026-04-22",
        "hold_date": "2026-04-27",
        "po_amount": 45000.0,
        "lc_amount": 45000.0,
        "gd_declared_value": 45000.0,
        "po_hs_code": "6109.10",
        "gd_hs_code": "6109.10",
        "bl_weight": 14200,
        "gd_weight": 14200,
        "lc_requires_inspection": False,
        "discrepancy": "none"
    },
    {
        "shipment_id": "SHP-08",
        "tenant_id": "exp_b",
        "port": "Karachi Port",
        "po_number": "PO-9848",
        "container_id": "C-409",
        "lc_number": "LC-2298",
        "gd_number": "GD-5517",
        "product_key": "terry_towels",
        "buyer_idx": 3,
        "vessel": "MV Karakoram Pearl",
        "voyage": "V-3310",
        "po_date": "2026-03-18",
        "lc_date": "2026-03-26",
        "lc_expiry": "2026-06-10",
        "bl_date": "2026-04-28",
        "gd_date": "2026-04-25",
        "hold_date": "2026-04-30",
        "po_amount": 52000.0,
        "lc_amount": 52000.0,
        "gd_declared_value": 52000.0,
        "po_hs_code": "6302.60",
        "gd_hs_code": "6302.60",
        "bl_weight": 12500,
        "gd_weight": 12500,
        "lc_requires_inspection": False,
        "discrepancy": "none"
    },
    {
        "shipment_id": "SHP-09",
        "tenant_id": "exp_c",
        "port": "Port Qasim",
        "po_number": "PO-9849",
        "container_id": "C-410",
        "lc_number": "LC-2299",
        "gd_number": "GD-5518",
        "product_key": "denim_trousers",
        "buyer_idx": 0,
        "vessel": "MV Sindh Star",
        "voyage": "V-5513",
        "po_date": "2026-03-20",
        "lc_date": "2026-03-28",
        "lc_expiry": "2026-06-15",
        "bl_date": "2026-04-30",
        "gd_date": "2026-04-28",
        "hold_date": "2026-05-02",
        "po_amount": 64000.0,
        "lc_amount": 64000.0,
        "gd_declared_value": 64000.0,
        "po_hs_code": "6203.42",
        "gd_hs_code": "6203.42",
        "bl_weight": 9800,
        "gd_weight": 9800,
        "lc_requires_inspection": False,
        "discrepancy": "none"
    },
    {
        "shipment_id": "SHP-10",
        "tenant_id": "exp_a",
        "port": "Karachi Port",
        "po_number": "PO-9850",
        "container_id": "C-411",
        "lc_number": "LC-2300",
        "gd_number": "GD-5519",
        "product_key": "cotton_tshirts",
        "buyer_idx": 1,
        "vessel": "MV Orient Crest",
        "voyage": "V-0822",
        "po_date": "2026-03-22",
        "lc_date": "2026-03-30",
        "lc_expiry": "2026-06-20",
        "bl_date": "2026-05-03",
        "gd_date": "2026-04-30",
        "hold_date": "2026-05-05",
        "po_amount": 45000.0,
        "lc_amount": 45000.0,
        "gd_declared_value": 45000.0,
        "po_hs_code": "6109.10",
        "gd_hs_code": "6109.10",
        "bl_weight": 14200,
        "gd_weight": 14200,
        "lc_requires_inspection": False,
        "discrepancy": "none"
    }
]

# ReportLab Styling Setup
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=15,
    leading=18,
    textColor=colors.HexColor('#1A365D'),
    alignment=1, # Center
    spaceAfter=8
)

subtitle_style = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=13,
    textColor=colors.HexColor('#2C5282'),
    alignment=1, # Center
    spaceAfter=12
)

section_heading = ParagraphStyle(
    'SectionHeading',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=13,
    textColor=colors.HexColor('#1A202C'),
    spaceBefore=6,
    spaceAfter=4
)

cell_style = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor('#2D3748')
)

cell_bold = ParagraphStyle(
    'TableCellBold',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor('#1A202C')
)

cell_header = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8.5,
    leading=11,
    textColor=colors.white
)

notice_body_style = ParagraphStyle(
    'NoticeBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=14,
    textColor=colors.HexColor('#1A202C')
)

def create_purchase_order_pdf(cfg, out_path):
    tenant = TENANTS[cfg["tenant_id"]]
    buyer = BUYERS[cfg["buyer_idx"]]
    prod = PRODUCTS[cfg["product_key"]]

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []

    story.append(Paragraph("PURCHASE ORDER", title_style))
    story.append(Paragraph(f"Official Commercial Contract & Order Confirmation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2C5282'), spaceAfter=10))

    meta_table_data = [
        [Paragraph(f"<b>PO Number:</b> {cfg['po_number']}", cell_style),
         Paragraph(f"<b>Date:</b> {cfg['po_date']}", cell_style)],
        [Paragraph(f"<b>Payment Terms:</b> Irrevocable LC at Sight", cell_style),
         Paragraph(f"<b>Trade Terms:</b> FOB {cfg['port']}", cell_style)],
        [Paragraph(f"<b>Port of Loading:</b> {cfg['port']}, Pakistan", cell_style),
         Paragraph(f"<b>Port of Discharge:</b> {buyer['port']}, {buyer['country']}", cell_style)]
    ]
    meta_table = Table(meta_table_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    parties_data = [
        [Paragraph("<b>BUYER / IMPORTER</b>", cell_bold), Paragraph("<b>SUPPLIER / EXPORTER</b>", cell_bold)],
        [Paragraph(f"{buyer['name']}<br/>{buyer['address']}<br/>Destination: {buyer['country']}", cell_style),
         Paragraph(f"{tenant['name']}<br/>{tenant['address']}<br/>NTN: {tenant['ntn']}<br/>Email: {tenant['email']}", cell_style)]
    ]
    parties_table = Table(parties_data, colWidths=[270, 270])
    parties_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("ORDER MERCHANDISE SPECIFICATIONS", section_heading))
    items_header = [
        Paragraph("Item", cell_header),
        Paragraph("Product Description", cell_header),
        Paragraph("HS Code", cell_header),
        Paragraph("Quantity", cell_header),
        Paragraph("Unit Price (USD)", cell_header),
        Paragraph("Total Value (USD)", cell_header)
    ]
    qty_val = prod["default_qty"]
    unit_price = cfg["po_amount"] / qty_val

    items_row = [
        Paragraph("1", cell_style),
        Paragraph(prod["description"], cell_style),
        Paragraph(cfg["po_hs_code"], cell_bold),
        Paragraph(f"{qty_val:,} {prod['unit']}", cell_style),
        Paragraph(f"${unit_price:.2f}", cell_style),
        Paragraph(f"${cfg['po_amount']:,.2f}", cell_bold)
    ]
    total_row = [
        Paragraph("<b>TOTAL</b>", cell_bold),
        Paragraph(f"Packaging: {prod['package_type']}", cell_style),
        Paragraph("", cell_style),
        Paragraph(f"{qty_val:,} {prod['unit']}", cell_bold),
        Paragraph("", cell_style),
        Paragraph(f"<b>USD {cfg['po_amount']:,.2f}</b>", cell_bold)
    ]

    items_table = Table([items_header, items_row, total_row], colWidths=[35, 205, 65, 75, 75, 85])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C5282')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#EDF2F7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 12))

    terms_p = Paragraph(
        f"<b>Special Instructions & Terms:</b><br/>"
        f"1. Goods must be manufactured and packaged strictly in accordance with approved export specifications.<br/>"
        f"2. Shipment must be delivered to {cfg['port']} for loading on container {cfg['container_id']}.<br/>"
        f"3. All shipping documentation including WeBOC Goods Declaration and Bill of Lading must strictly cite Purchase Order {cfg['po_number']}.<br/>"
        f"4. Payment shall be executed through Documentary Letter of Credit referencing this PO Number.",
        cell_style
    )
    story.append(terms_p)
    doc.build(story)


def create_bill_of_lading_pdf(cfg, out_path):
    tenant = TENANTS[cfg["tenant_id"]]
    buyer = BUYERS[cfg["buyer_idx"]]
    prod = PRODUCTS[cfg["product_key"]]

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []

    story.append(Paragraph("OCEAN BILL OF LADING", title_style))
    story.append(Paragraph("COMBINED TRANSPORT BILL OF LADING / NON-NEGOTIABLE COPY", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2C5282'), spaceAfter=8))

    meta_rows = [
        [Paragraph(f"<b>B/L Number:</b> BL-{cfg['po_number'].replace('PO-', '')}-EXP", cell_style),
         Paragraph(f"<b>Shipped on Board Date:</b> {cfg['bl_date']}", cell_bold)],
        [Paragraph(f"<b>Ocean Vessel:</b> {cfg['vessel']}", cell_style),
         Paragraph(f"<b>Voyage Number:</b> {cfg['voyage']}", cell_style)],
        [Paragraph(f"<b>Port of Loading:</b> {cfg['port']}, Pakistan", cell_style),
         Paragraph(f"<b>Port of Discharge:</b> {buyer['port']}, {buyer['country']}", cell_style)]
    ]
    meta_table = Table(meta_rows, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    parties_data = [
        [Paragraph("<b>SHIPPER / EXPORTER</b>", cell_bold), Paragraph("<b>CONSIGNEE</b>", cell_bold)],
        [Paragraph(f"{tenant['name']}<br/>{tenant['address']}<br/>Pakistan", cell_style),
         Paragraph(f"To Order of {buyer['bank']}<br/>Notify: {buyer['name']}<br/>{buyer['address']}", cell_style)]
    ]
    parties_table = Table(parties_data, colWidths=[270, 270])
    parties_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("CONTAINER & CARGO PARTICULARS", section_heading))
    cargo_header = [
        Paragraph("Container No.", cell_header),
        Paragraph("Marks & Numbers", cell_header),
        Paragraph("No. of Packages & Description of Goods", cell_header),
        Paragraph("Gross Weight", cell_header),
        Paragraph("Measurement", cell_header)
    ]
    cargo_row = [
        Paragraph(f"<b>{cfg['container_id']}</b><br/>Seal: SL-99201", cell_bold),
        Paragraph(f"{cfg['po_number']}<br/>{cfg['container_id']}<br/>MADE IN PAKISTAN", cell_style),
        Paragraph(f"{prod['package_type']} STC:<br/>{prod['description']}<br/>Clean on Board", cell_style),
        Paragraph(f"<b>{cfg['bl_weight']:,} KG</b>", cell_bold),
        Paragraph("45.00 CBM", cell_style)
    ]
    cargo_table = Table([cargo_header, cargo_row], colWidths=[90, 105, 205, 80, 60])
    cargo_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C5282')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(cargo_table)
    story.append(Spacer(1, 10))

    freight_p = Paragraph(
        f"<b>Freight & Charges:</b> Freight Prepaid. Shipped on Board in apparent good order and condition.<br/>"
        f"Carrier acknowledges receipt of container {cfg['container_id']} with gross weight {cfg['bl_weight']:,} KG "
        f"loaded at {cfg['port']} for carriage on vessel {cfg['vessel']} voyage {cfg['voyage']}.",
        cell_style
    )
    story.append(freight_p)
    doc.build(story)


def create_letter_of_credit_pdf(cfg, out_path):
    tenant = TENANTS[cfg["tenant_id"]]
    buyer = BUYERS[cfg["buyer_idx"]]
    prod = PRODUCTS[cfg["product_key"]]

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []

    story.append(Paragraph("DOCUMENTARY LETTER OF CREDIT", title_style))
    story.append(Paragraph("IRREVOCABLE DOCUMENTARY CREDIT - SWIFT MT700 TRANSMISSION", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2C5282'), spaceAfter=8))

    lc_meta = [
        [Paragraph(f"<b>Documentary Credit Number (20):</b> {cfg['lc_number']}", cell_bold),
         Paragraph(f"<b>Date of Issue (31C):</b> {cfg['lc_date']}", cell_style)],
        [Paragraph(f"<b>Date and Place of Expiry (31D):</b> {cfg['lc_expiry']} Pakistan", cell_bold),
         Paragraph(f"<b>Credit Amount (32B):</b> USD {cfg['lc_amount']:,.2f}", cell_bold)],
        [Paragraph(f"<b>Issuing Bank (51A):</b> {buyer['bank']} (SWIFT: {buyer['bank_swift']})", cell_style),
         Paragraph(f"<b>Available with (41D):</b> Any Bank in Pakistan by Negotiation", cell_style)]
    ]
    lc_table = Table(lc_meta, colWidths=[270, 270])
    lc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(lc_table)
    story.append(Spacer(1, 8))

    parties = [
        [Paragraph("<b>APPLICANT (50)</b>", cell_bold), Paragraph("<b>BENEFICIARY (59)</b>", cell_bold)],
        [Paragraph(f"{buyer['name']}<br/>{buyer['address']}", cell_style),
         Paragraph(f"{tenant['name']}<br/>{tenant['address']}<br/>NTN: {tenant['ntn']}", cell_style)]
    ]
    parties_tbl = Table(parties, colWidths=[270, 270])
    parties_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(parties_tbl)
    story.append(Spacer(1, 8))

    shipment_info = [
        [Paragraph(f"<b>Port of Loading (44E):</b> {cfg['port']}, Pakistan", cell_style),
         Paragraph(f"<b>Port of Discharge (44F):</b> {buyer['port']}, {buyer['country']}", cell_style)],
        [Paragraph(f"<b>Partial Shipments (43P):</b> Not Allowed", cell_style),
         Paragraph(f"<b>Transshipment (43T):</b> Not Allowed", cell_style)],
        [Paragraph(f"<b>Description of Goods (45A):</b> {prod['description']} under Purchase Order {cfg['po_number']}", cell_style),
         Paragraph(f"<b>Container Requirement:</b> Container {cfg['container_id']}", cell_style)]
    ]
    ship_tbl = Table(shipment_info, colWidths=[270, 270])
    ship_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(ship_tbl)
    story.append(Spacer(1, 10))

    story.append(Paragraph("DOCUMENTS REQUIRED (FIELD 46A)", section_heading))
    doc_items = [
        f"1. Signed Commercial Invoice in 3 originals and 3 copies citing Purchase Order {cfg['po_number']} and Letter of Credit {cfg['lc_number']}.",
        f"2. Full set (3/3) original clean on board ocean Bills of Lading consigned to order of {buyer['bank']} marked freight prepaid.",
        f"3. Packing List in 3 originals showing gross and net weight, carton numbers, and container reference {cfg['container_id']}.",
        f"4. Certificate of Origin issued by the Karachi Chamber of Commerce and Industry."
    ]
    if cfg["lc_requires_inspection"]:
        doc_items.append(
            "5. Pre-Shipment Inspection Certificate issued by an authorized independent surveyor (SGS or Bureau Veritas) "
            "certifying strict compliance with fabric quality, stitching, and packaging standards."
        )

    for item in doc_items:
        story.append(Paragraph(item, cell_style))
        story.append(Spacer(1, 3))

    doc.build(story)


def create_weboc_gd_pdf(cfg, out_path):
    tenant = TENANTS[cfg["tenant_id"]]
    buyer = BUYERS[cfg["buyer_idx"]]
    prod = PRODUCTS[cfg["product_key"]]

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []

    story.append(Paragraph("PAKISTAN CUSTOMS - WeBOC GOODS DECLARATION (EXPORT)", title_style))
    story.append(Paragraph("WEB-BASED ONE CUSTOMS ELECTRONIC CLEARANCE SYSTEM", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2C5282'), spaceAfter=8))

    gd_meta = [
        [Paragraph(f"<b>GD Number:</b> {cfg['gd_number']}", cell_bold),
         Paragraph(f"<b>GD Date:</b> {cfg['gd_date']}", cell_style)],
        [Paragraph(f"<b>Collectorate:</b> Model Customs Collectorate (Export) - {cfg['port']}", cell_style),
         Paragraph(f"<b>Declaration Type:</b> Commercial Export (Normal)", cell_style)],
        [Paragraph(f"<b>Linked PO:</b> {cfg['po_number']}", cell_style),
         Paragraph(f"<b>Linked LC / Financial Doc:</b> {cfg['lc_number']}", cell_style)]
    ]
    gd_tbl = Table(gd_meta, colWidths=[270, 270])
    gd_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(gd_tbl)
    story.append(Spacer(1, 8))

    parties = [
        [Paragraph("<b>EXPORTER DETAILS</b>", cell_bold), Paragraph("<b>CONSIGNEE / BUYER DETAILS</b>", cell_bold)],
        [Paragraph(f"{tenant['name']}<br/>NTN: {tenant['ntn']}<br/>{tenant['address']}", cell_style),
         Paragraph(f"{buyer['name']}<br/>Destination Country: {buyer['country']}<br/>Port: {buyer['port']}", cell_style)]
    ]
    parties_tbl = Table(parties, colWidths=[270, 270])
    parties_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EDF2F7')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(parties_tbl)
    story.append(Spacer(1, 10))

    story.append(Paragraph("DECLARED GOODS & VALUATION PARTICULARS", section_heading))
    items_header = [
        Paragraph("Item", cell_header),
        Paragraph("Declared HS Code", cell_header),
        Paragraph("Goods Description", cell_header),
        Paragraph("Declared Quantity", cell_header),
        Paragraph("Declared FOB Value", cell_header),
        Paragraph("Gross Weight", cell_header)
    ]
    items_row = [
        Paragraph("1", cell_style),
        Paragraph(f"<b>{cfg['gd_hs_code']}</b>", cell_bold),
        Paragraph(prod["description"], cell_style),
        Paragraph(f"{prod['default_qty']:,} {prod['unit']}", cell_style),
        Paragraph(f"<b>USD {cfg['gd_declared_value']:,.2f}</b>", cell_bold),
        Paragraph(f"<b>{cfg['gd_weight']:,} KG</b>", cell_bold)
    ]
    items_table = Table([items_header, items_row], colWidths=[30, 80, 185, 75, 95, 75])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2C5282')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    shipping_box = [
        [Paragraph(f"<b>Port of Shipment:</b> {cfg['port']}", cell_style),
         Paragraph(f"<b>Container ID:</b> {cfg['container_id']}", cell_bold)],
        [Paragraph(f"<b>Carrying Vessel:</b> {cfg['vessel']}", cell_style),
         Paragraph(f"<b>System Status:</b> Submitted - Assigned to Scrutiny / Review", cell_style)]
    ]
    ship_tbl = Table(shipping_box, colWidths=[270, 270])
    ship_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(ship_tbl)
    doc.build(story)


def create_customs_hold_notice_pdf(cfg, out_path):
    tenant = TENANTS[cfg["tenant_id"]]

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []

    story.append(Paragraph("PAKISTAN CUSTOMS SERVICE", title_style))
    story.append(Paragraph("MODEL CUSTOMS COLLECTORATE - OFFICIAL HOLD & REVIEW NOTICE", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#C53030'), spaceAfter=10))

    notice_meta = [
        [Paragraph(f"<b>Notice Reference:</b> CHN-{cfg['gd_number'].replace('GD-', '')}-REV", cell_bold),
         Paragraph(f"<b>Issue Date:</b> {cfg['hold_date']}", cell_style)],
        [Paragraph(f"<b>Station / Location:</b> Export Terminal, {cfg['port']}", cell_style),
         Paragraph(f"<b>Issuing Authority:</b> Appraisal & Scrutiny Wing", cell_style)],
        [Paragraph(f"<b>Purchase Order Mentioned:</b> {cfg['po_number']}", cell_bold),
         Paragraph(f"<b>Goods Declaration Mentioned:</b> {cfg['gd_number']}", cell_bold)],
        [Paragraph(f"<b>Container Mentioned:</b> {cfg['container_id']}", cell_style),
         Paragraph(f"<b>Exporter:</b> {tenant['name']} (NTN: {tenant['ntn']})", cell_style)]
    ]
    meta_table = Table(notice_meta, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF5F5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#FEB2B2')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FED7D7')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    body_text = (
        f"<b>NOTICE OF CONSIGNMENT DETENTION / DOCUMENTARY HOLD</b><br/><br/>"
        f"This official notice is issued to notify the exporter, carrier, and terminal operator that the export consignment "
        f"covered under WeBOC Goods Declaration <b>{cfg['gd_number']}</b>, corresponding to Purchase Order <b>{cfg['po_number']}</b> "
        f"and loaded into Container <b>{cfg['container_id']}</b>, has been placed on administrative hold at {cfg['port']}.<br/><br/>"
        f"The shipment documentation and declarations are currently under review by customs appraisal authorities in accordance with "
        f"standard customs regulatory compliance procedures. Gate-out authorization and terminal loading permission remain suspended "
        f"while documents are under review.<br/><br/>"
        f"Further formal notifications will follow upon completion of the documentary review process."
    )
    story.append(Paragraph(body_text, notice_body_style))
    story.append(Spacer(1, 16))

    signature_data = [
        [Paragraph("<b>Appraising Officer</b><br/>Export Assessment Section<br/>Pakistan Customs", cell_style),
         Paragraph("<b>Assistant Collector of Customs</b><br/>Model Customs Collectorate<br/>Islamic Republic of Pakistan", cell_style)]
    ]
    sig_table = Table(signature_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('LINEBEFORE', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sig_table)

    doc.build(story)


def main():
    print(f"Generating synthetic textile export dataset in: {BASE_DIR}")

    # Ensure target directories exist
    PDFS_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    metadata_list = []
    ground_truth_dict = {}

    for cfg in SHIPMENTS_CONFIG:
        shipment_id = cfg["shipment_id"]
        shp_pdf_dir = PDFS_DIR / shipment_id
        shp_pdf_dir.mkdir(parents=True, exist_ok=True)

        print(f"Generating documents for shipment: {shipment_id} (Tenant: {cfg['tenant_id']}, Port: {cfg['port']})...")

        # 5 PDF file paths
        po_path = shp_pdf_dir / "purchase_order.pdf"
        bl_path = shp_pdf_dir / "bill_of_lading.pdf"
        lc_path = shp_pdf_dir / "letter_of_credit.pdf"
        gd_path = shp_pdf_dir / "goods_declaration.pdf"
        hold_path = shp_pdf_dir / "customs_hold_notice.pdf"

        # Generate each PDF
        create_purchase_order_pdf(cfg, po_path)
        create_bill_of_lading_pdf(cfg, bl_path)
        create_letter_of_credit_pdf(cfg, lc_path)
        create_weboc_gd_pdf(cfg, gd_path)
        create_customs_hold_notice_pdf(cfg, hold_path)

        # Metadata entries for the 5 PDFs
        doc_definitions = [
            ("purchase_order", "DOC-" + shipment_id.replace('-', '') + "-PO", po_path, f"{cfg['po_date']}T09:00:00Z"),
            ("bill_of_lading", "DOC-" + shipment_id.replace('-', '') + "-BL", bl_path, f"{cfg['bl_date']}T14:30:00Z"),
            ("letter_of_credit", "DOC-" + shipment_id.replace('-', '') + "-LC", lc_path, f"{cfg['lc_date']}T11:15:00Z"),
            ("goods_declaration", "DOC-" + shipment_id.replace('-', '') + "-GD", gd_path, f"{cfg['gd_date']}T16:00:00Z"),
            ("customs_hold_notice", "DOC-" + shipment_id.replace('-', '') + "-CHN", hold_path, f"{cfg['hold_date']}T10:00:00Z")
        ]

        for doc_type, doc_id, file_p, ts in doc_definitions:
            rel_path = file_p.relative_to(BASE_DIR).as_posix()
            entry = {
                "doc_id": doc_id,
                "doc_type": doc_type,
                "shipment_id": shipment_id,
                "tenant_id": cfg["tenant_id"],
                "access_level": "standard",
                "port": cfg["port"],
                "timestamp": ts,
                "version": "1.0",
                "file_path": rel_path
            }
            metadata_list.append(entry)

        # Ground truth entry
        ground_truth_dict[shipment_id] = {
            "shipment_id": shipment_id,
            "po_number": cfg["po_number"],
            "po_id": cfg["po_number"],
            "container_id": cfg["container_id"],
            "container_number": cfg["container_id"],
            "lc_number": cfg["lc_number"],
            "lc_id": cfg["lc_number"],
            "gd_number": cfg["gd_number"],
            "gd_id": cfg["gd_number"],
            "tenant_id": cfg["tenant_id"],
            "port": cfg["port"],
            "product": PRODUCTS[cfg["product_key"]]["name"],
            "hs_code": PRODUCTS[cfg["product_key"]]["hs_code"],
            "discrepancy": cfg["discrepancy"]
        }

    # Write metadata.json
    metadata_path = SYNTHETIC_DIR / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2)
    print(f"Wrote {len(metadata_list)} entries to {metadata_path}")

    # Write ground_truth_shipments.json
    gt_path = EVAL_DIR / "ground_truth_shipments.json"
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth_dict, f, indent=2)
    print(f"Wrote ground truth for {len(ground_truth_dict)} shipments to {gt_path}")

    print("Synthetic data generation completed successfully!")

if __name__ == "__main__":
    main()
