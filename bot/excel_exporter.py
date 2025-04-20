from openpyxl import Workbook
from datetime import datetime
import os

def export_complaints_to_excel(complaints, output_dir="exports"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/complaints_{timestamp}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Complaints"

    ws.append(["ID", "ФИО", "Телефон", "Комментарий", "Дата"])

    for c in complaints:
        ws.append([c.id, c.full_name, c.phone, c.comment, c.created_at.strftime("%Y-%m-%d %H:%M")])

    wb.save(filename)
    return filename
