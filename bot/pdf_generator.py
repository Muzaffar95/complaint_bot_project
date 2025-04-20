from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime

def generate_pdf(fio, phone, comment, output_dir="pdfs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/complaint_{timestamp}.pdf"
    
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 14)
    c.drawString(50, height - 50, "Жалоба:")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"ФИО: {fio}")
    c.drawString(50, height - 130, f"Телефон: {phone}")
    c.drawString(50, height - 160, "Комментарий:")
    text_object = c.beginText(50, height - 190)
    text_object.setFont("Helvetica", 12)
    for line in comment.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)
    
    c.save()
    return filename
