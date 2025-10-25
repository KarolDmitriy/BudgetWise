import pandas as pd
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

REPORTS = Path("reports")
REPORTS.mkdir(exist_ok=True)

def export_excel(df_ops, filename=None):
    if filename is None:
        filename = REPORTS / f"budget_report_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    else:
        filename = Path(filename)
    # save
    df_ops.to_excel(filename, index=False)
    return filename

def export_pdf(df_ops, filename=None):
    if filename is None:
        filename = REPORTS / f"budget_report_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    else:
        filename = Path(filename)
    c = canvas.Canvas(str(filename), pagesize=A4)
    width, height = A4
    margin = 15*mm
    x = margin
    y = height - margin
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "BudgetWise — Отчёт по операциям")
    y -= 10*mm
    c.setFont("Helvetica", 10)
    # header
    headers = ["Дата","Сумма","Категория","Примечание"]
    col_widths = [40*mm, 35*mm, 60*mm, width - margin*2 - 135*mm]
    # table header
    c.setFont("Helvetica-Bold", 9)
    cx = x
    for i, h in enumerate(headers):
        c.drawString(cx, y, h)
        cx += col_widths[i]
    y -= 6*mm
    c.setFont("Helvetica", 9)
    for idx, row in df_ops.iterrows():
        if y < margin + 30*mm:
            c.showPage()
            y = height - margin
        cx = x
        c.drawString(cx, y, str(row.get("date",""))[:10]); cx += col_widths[0]
        c.drawString(cx, y, f"{row.get('amount',0):.2f}"); cx += col_widths[1]
        c.drawString(cx, y, str(row.get("category",""))[:30]); cx += col_widths[2]
        c.drawString(cx, y, str(row.get("note",""))[:80])
        y -= 6*mm
    c.save()
    return filename
