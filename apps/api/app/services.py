import os
from datetime import datetime
from uuid import uuid4

from reportlab.lib.pagesizes import letter
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
    def generate_quote_pdf(self, tenant_name: str, quote_id: int, customer_name: str, total: float, line_items: list[dict]):
        os.makedirs(settings.pdf_output_dir, exist_ok=True)
        filename = f"quote_{quote_id}_{uuid4().hex[:8]}.pdf"
        path = os.path.join(settings.pdf_output_dir, filename)

        c = canvas.Canvas(path, pagesize=letter)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(72, 750, f"{tenant_name} - Quote #{quote_id}")
        c.setFont("Helvetica", 12)
        c.drawString(72, 725, f"Customer: {customer_name}")
        c.drawString(72, 710, f"Total: ${total:,.2f}")

        y = 680
        for item in line_items:
            c.drawString(72, y, f"- {item['label']}: ${float(item['amount']):,.2f}")
            y -= 18
            if y < 80:
                c.showPage()
                y = 750

        c.showPage()
        c.save()
        return path
