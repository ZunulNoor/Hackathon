from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

def export_to_pdf(structured_data, explanations, summary_text, filename="report_summary.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    y = height - 40
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Medical Report Summary")
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(40, y, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 40

    for _, row in structured_data.iterrows():
        if y < 100:
            c.showPage()
            y = height - 40

        c.setFont("Helvetica-Bold", 11)
        c.drawString(40, y, f"{row['Test']}: {row['Value']} {row['Unit']} (Normal: {row['Normal Range']})")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Flag: {row['Flag']}")
        y -= 15

        explanation = explanations.get(row['Test'], "")
        for line in explanation.split('\n'):
            c.drawString(60, y, line)
            y -= 12

        y -= 10

    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Overall Health Summary & Suggestions:")
    y -= 20
    c.setFont("Helvetica", 10)

    for line in summary_text.split('\n'):
        if y < 100:
            c.showPage()
            y = height - 40
        c.drawString(60, y, line)
        y -= 12

    c.save()
