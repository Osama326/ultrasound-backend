from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.core.config import settings


def build_report_pdf(report, doctor_name: str) -> str:
    relative_path = Path(settings.generated_report_dir) / f"report_{report.id}.pdf"
    absolute_path = settings.base_dir / relative_path

    c = canvas.Canvas(str(absolute_path), pagesize=A4)
    width, height = A4
    y = height - 60

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Jeejal AI Report")
    y -= 35

    c.setFont("Helvetica", 11)
    notes = report.clinical_notes or ""
    lines = [
        f"Patient: {report.patient_name}",
        f"Age: {report.patient_age}",
        f"Identifier: {report.patient_identifier}",
        f"Parity: {_extract_note_value(notes, 'Parity') or 'Not provided'}",
        f"LMP: {_extract_note_value(notes, 'LMP') or 'Not provided'}",
        f"Medical History: {_extract_note_value(notes, 'Medical History') or 'Not provided'}",
        "",
        "AI Report:",
        report.ai_report_text or "",
        "",
        "Doctor Diagnosis:",
        report.doctor_diagnosis or "No doctor diagnosis provided.",
        "",
    ]

    for line in lines:
        for wrapped in _wrap_text(line, 90):
            c.drawString(50, y, wrapped)
            y -= 16
            if y < 170:
                c.showPage()
                y = height - 60
                c.setFont("Helvetica", 11)

    signature_bottom_y = 72
    if report.signature_path:
        signature_file = settings.upload_path / report.signature_path
        if signature_file.exists():
            c.drawImage(
                ImageReader(str(signature_file)),
                50,
                signature_bottom_y + 20,
                width=140,
                height=50,
                preserveAspectRatio=True,
                mask="auto",
            )

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, signature_bottom_y, f"Dr. {doctor_name}")

    c.save()
    return str(relative_path).replace("\\", "/")


def _wrap_text(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]

    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        tentative = f"{current} {word}".strip()
        if len(tentative) <= max_len:
            current = tentative
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _extract_note_value(notes: str, label: str) -> str:
    for line in notes.splitlines():
        if line.lower().startswith(f"{label.lower()}:"):
            return line.split(":", 1)[1].strip()
    return ""
