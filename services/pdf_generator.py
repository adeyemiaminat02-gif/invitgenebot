import os
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_invoice(invoice_data: dict, output_path: str) -> str:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []
    styles = getSampleStyleSheet()

    # Title & Header
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor("#1A365D"))
    story.append(Paragraph(f"INVOICE #{invoice_data['invoice_number']}", title_style))
    story.append(Spacer(1, 12))

    # Business vs Customer Details Table
    biz_info = f"<b>{invoice_data.get('business_name', 'Company')}</b><br/>" \
               f"Email: {invoice_data.get('business_email', 'N/A')}<br/>" \
               f"Phone: {invoice_data.get('business_phone', 'N/A')}<br/>" \
               f"{invoice_data.get('business_address', '')}"

    cust_info = f"<b>Billed To:</b><br/>" \
                f"{invoice_data.get('customer_name', 'Customer')}<br/>" \
                f"Email: {invoice_data.get('customer_email', 'N/A')}<br/>" \
                f"{invoice_data.get('customer_address', '')}"

    info_table_data = [[Paragraph(biz_info, styles['Normal']), Paragraph(cust_info, styles['Normal'])]]
    info_table = Table(info_table_data, colWidths=[270, 270])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # Items Table
    table_data = [["Description", "Qty", "Unit Price", "Total"]]
    for item in invoice_data.get('items', []):
        qty = item['quantity']
        price = item['unit_price']
        total = qty * price
        table_data.append([
            item['description'],
            str(qty),
            f"{invoice_data.get('currency', 'USD')} {price:.2f}",
            f"{invoice_data.get('currency', 'USD')} {total:.2f}"
        ])

    items_table = Table(table_data, colWidths=[260, 60, 110, 110])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))

    # Totals Summary
    tot_data = [
        ["Subtotal:", f"{invoice_data.get('currency', 'USD')} {invoice_data.get('subtotal', 0.0):.2f}"],
        ["Grand Total:", f"{invoice_data.get('currency', 'USD')} {invoice_data.get('grand_total', 0.0):.2f}"]
    ]
    tot_table = Table(tot_data, colWidths=[430, 110])
    tot_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))
    story.append(tot_table)
    story.append(Spacer(1, 20))

    # Notes & Payment Info
    if invoice_data.get('notes'):
        story.append(Paragraph(f"<b>Notes:</b> {invoice_data['notes']}", styles['Normal']))

    doc.build(story)
    return output_path
