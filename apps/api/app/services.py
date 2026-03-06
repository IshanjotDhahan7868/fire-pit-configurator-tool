import os
from datetime import datetime
from uuid import uuid4

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from .config import settings


class EmailService:
    def send_quote_received(self, tenant_slug: str, email: str, summary: str):
        os.makedirs(settings.email_output_dir, exist_ok=True)
        filename = f"{tenant_slug}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:6]}.txt"
        path = os.path.join(settings.email_output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"To: {email}\nSubject: Quote Request Received\n\n{summary}\n")
        return path


class PDFService:
    def generate_quote_pdf(
        self,
        tenant_name: str,
        quote_id: int,
        customer_name: str,
        total: float,
        line_items: list[dict],
        brand_primary: str = "#ea580c",
        brand_secondary: str = "#1f2937",
    ):
        os.makedirs(settings.pdf_output_dir, exist_ok=True)
        filename = f"quote_{quote_id}_{uuid4().hex[:8]}.pdf"
        path = os.path.join(settings.pdf_output_dir, filename)

        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter

        # Header band
        c.setFillColor(colors.HexColor(brand_secondary))
        c.rect(0, height - 1.2 * inch, width, 1.2 * inch, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(0.75 * inch, height - 0.75 * inch, tenant_name)
        c.setFont("Helvetica", 11)
        c.drawString(0.75 * inch, height - 1.02 * inch, f"Quote #{quote_id} • Generated {datetime.utcnow():%Y-%m-%d}")

        # Meta
        c.setFillColor(colors.HexColor(brand_primary))
        c.setFont("Helvetica-Bold", 13)
        c.drawString(0.75 * inch, height - 1.7 * inch, "Prepared for")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(0.75 * inch, height - 1.95 * inch, customer_name)

        c.setFillColor(colors.HexColor(brand_primary))
        c.setFont("Helvetica-Bold", 13)
        c.drawString(4.3 * inch, height - 1.7 * inch, "Quote Total")
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(4.3 * inch, height - 1.95 * inch, f"${total:,.2f}")

        # Table header
        y = height - 2.4 * inch
        c.setFillColor(colors.HexColor(brand_secondary))
        c.rect(0.75 * inch, y, 6.0 * inch, 0.35 * inch, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(0.9 * inch, y + 0.12 * inch, "Description")
        c.drawRightString(6.55 * inch, y + 0.12 * inch, "Amount")

        y -= 0.32 * inch
        c.setFont("Helvetica", 11)
        for item in line_items:
            if y < 1.2 * inch:
                c.showPage()
                y = height - 1.0 * inch
            c.setFillColor(colors.black)
            c.drawString(0.9 * inch, y, str(item["label"]))
            c.drawRightString(6.55 * inch, y, f"${float(item['amount']):,.2f}")
            y -= 0.26 * inch

        c.setStrokeColor(colors.HexColor(brand_primary))
        c.line(0.75 * inch, y - 0.05 * inch, 6.75 * inch, y - 0.05 * inch)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.9 * inch, y - 0.3 * inch, "Grand Total")
        c.drawRightString(6.55 * inch, y - 0.3 * inch, f"${total:,.2f}")

        c.setFont("Helvetica", 9)
        c.setFillColor(colors.grey)
        c.drawString(0.75 * inch, 0.65 * inch, "This quote is valid for 30 days and subject to final site inspection.")

        c.save()
        return path
