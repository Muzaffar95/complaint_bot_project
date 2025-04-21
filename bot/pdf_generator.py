# from reportlab.lib.pagesizes import A4
# from reportlab.pdfgen import canvas
# import os
# from datetime import datetime
#
# def generate_pdf(fio, phone, comment, output_dir="pdfs"):
#     os.makedirs(output_dir, exist_ok=True)
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = f"{output_dir}/complaint_{timestamp}.pdf"
#
#     c = canvas.Canvas(filename, pagesize=A4)
#     width, height = A4
#
#     c.setFont("Helvetica", 14)
#     c.drawString(50, height - 50, "Жалоба:")
#
#     c.setFont("Helvetica", 12)
#     c.drawString(50, height - 100, f"ФИО: {fio}")
#     c.drawString(50, height - 130, f"Телефон: {phone}")
#     c.drawString(50, height - 160, "Комментарий:")
#     text_object = c.beginText(50, height - 190)
#     text_object.setFont("Helvetica", 12)
#     for line in comment.splitlines():
#         text_object.textLine(line)
#     c.drawText(text_object)
#
#     c.save()
#     return filename


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from datetime import datetime
import os

def generate_pdf(fio, phone, comment, complaint_type="Публичная", output_dir="pdfs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/complaint_{timestamp}.pdf"

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawCentredString(width / 2, height - 50, "Заявление о жалобе")

    # Метаданные
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    y = height - 100
    line_spacing = 20

    c.drawString(50, y, f"Тип жалобы: {complaint_type}")
    c.drawString(50, y - line_spacing, f"ФИО: {fio}")
    c.drawString(50, y - 2 * line_spacing, f"Телефон: {phone}")
    c.drawString(50, y - 3 * line_spacing, f"Дата подачи: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    # Комментарий
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 5 * line_spacing, "Текст жалобы:")
    c.setFont("Helvetica", 11)

    text_obj = c.beginText(50, y - 6 * line_spacing)
    text_obj.setLeading(16)
    for line in comment.splitlines():
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Подпись
    c.setFont("Helvetica-Oblique", 10)
    c.drawRightString(width - 50, 40, "MDMGASN — Автоматизированная система жалоб")

    c.save()
    return filename
