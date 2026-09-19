from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


output_path = (
    Path(__file__).resolve().parents[1]
    / "sample_documents"
    / "sample.pdf"
)

output_path.parent.mkdir(parents=True, exist_ok=True)


pdf = canvas.Canvas(str(output_path), pagesize=A4)

pdf.setFont("Helvetica-Bold", 16)
pdf.drawString(72, 800, "Document Intelligence Test Paper")

pdf.setFont("Helvetica", 11)

questions = [
    "1. What is Python?",
    "A. A programming language",
    "B. A database",
    "C. An operating system",
    "D. A web browser",
    "",
    "2. Which data structure follows FIFO?",
    "A. Stack",
    "B. Queue",
    "C. Tree",
    "D. Graph",
    "",
    "3. Which protocol is commonly used for secure web communication?",
    "A. HTTP",
    "B. FTP",
    "C. HTTPS",
    "D. SMTP",
]

y = 760

for line in questions:
    pdf.drawString(72, y, line)
    y -= 22

pdf.save()

print(f"Created: {output_path}")