from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dependencies import get_current_user, require_doctor, require_provider
from app.models.report import Report, ReportStatus
from app.models.user import User
from app.schemas.report import (
    AssignDoctorRequest,
    RejectAndEditRequest,
    ReportCreateRequest,
    ReportResponse,
    SignReportRequest,
)
from app.services.ai_service import generate_ai_report
from app.services.pdf_service import build_report_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


def _get_report_or_404(db: Session, report_id: int) -> Report:
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("", response_model=ReportResponse)
def create_report(
    payload: ReportCreateRequest,
    provider: User = Depends(require_provider),
    db: Session = Depends(get_db),
):
    report = Report(provider_id=provider.id, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.post("/{report_id}/upload-image", response_model=ReportResponse)
def upload_ultrasound_image(
    report_id: int,
    image: UploadFile = File(...),
    provider: User = Depends(require_provider),
    db: Session = Depends(get_db),
):
    report = _get_report_or_404(db, report_id)
    if report.provider_id != provider.id:
        raise HTTPException(status_code=403, detail="You can only update your own reports")

    suffix = Path(image.filename or "scan.jpg").suffix or ".jpg"
    relative_path = Path("ultrasounds") / f"report_{report.id}_{uuid4().hex}{suffix}"
    absolute_path = settings.upload_path / relative_path
    absolute_path.write_bytes(image.file.read())

    report.image_path = str(relative_path).replace("\\", "/")
    db.commit()
    db.refresh(report)
    return report


@router.post("/{report_id}/analyze", response_model=ReportResponse)
def analyze_report(
    report_id: int,
    provider: User = Depends(require_provider),
    db: Session = Depends(get_db),
):
    report = _get_report_or_404(db, report_id)
    if report.provider_id != provider.id:
        raise HTTPException(status_code=403, detail="You can only analyze your own reports")
    if not report.image_path:
        raise HTTPException(status_code=400, detail="Upload an image first")

    result = generate_ai_report(settings.upload_path / report.image_path, report.patient_name)
    report.ai_report_text = result["report_text"]
    db.commit()
    db.refresh(report)
    return report


@router.post("/{report_id}/assign-doctor", response_model=ReportResponse)
def assign_doctor(
    report_id: int,
    payload: AssignDoctorRequest,
    provider: User = Depends(require_provider),
    db: Session = Depends(get_db),
):
    report = _get_report_or_404(db, report_id)
    if report.provider_id != provider.id:
        raise HTTPException(status_code=403, detail="You can only assign your own reports")
    if not report.ai_report_text:
        raise HTTPException(status_code=400, detail="Analyze the report before assigning a doctor")

    doctor = db.get(User, payload.doctor_id)
    if not doctor or doctor.role.value != "doctor":
        raise HTTPException(status_code=404, detail="Doctor not found")

    report.doctor_id = doctor.id
    report.assigned_doctor_name = doctor.full_name
    report.status = ReportStatus.pending_review.value
    db.commit()
    db.refresh(report)
    return report


@router.get("/provider/me", response_model=list[ReportResponse])
def provider_reports(
    status: str | None = Query(default=None),
    provider: User = Depends(require_provider),
    db: Session = Depends(get_db),
):
    query = db.query(Report).filter(Report.provider_id == provider.id)
    if status:
        query = query.filter(Report.status == status)
    return query.order_by(Report.updated_at.desc()).all()


@router.get("/doctor/me", response_model=list[ReportResponse])
def doctor_reports(
    status: str | None = Query(default=None),
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    query = db.query(Report).filter(Report.doctor_id == doctor.id)
    if status:
        query = query.filter(Report.status == status)
    return query.order_by(Report.updated_at.desc()).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_report_or_404(db, report_id)


@router.post("/{report_id}/accept-and-sign", response_model=ReportResponse)
def accept_and_sign(
    report_id: int,
    payload: SignReportRequest,
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    report = _get_report_or_404(db, report_id)
    if report.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="This report is not assigned to you")
    if not doctor.signature_path:
        raise HTTPException(status_code=400, detail="Upload or draw your signature first")

    if payload.report_text:
        report.ai_report_text = payload.report_text
    report.doctor_diagnosis = payload.doctor_diagnosis or report.doctor_diagnosis
    report.signature_path = doctor.signature_path
    report.signed_by_name = doctor.full_name
    report.signed_at = datetime.utcnow()
    report.status = ReportStatus.signed.value
    report.pdf_path = build_report_pdf(report, doctor.full_name)
    db.commit()
    db.refresh(report)
    return report


@router.post("/{report_id}/reject-and-edit", response_model=ReportResponse)
def reject_and_edit(
    report_id: int,
    payload: RejectAndEditRequest,
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    report = _get_report_or_404(db, report_id)
    if report.doctor_id != doctor.id:
        raise HTTPException(status_code=403, detail="This report is not assigned to you")
    if report.status == ReportStatus.signed.value:
        raise HTTPException(status_code=400, detail="Signed reports are locked")

    if payload.report_text:
        report.ai_report_text = payload.report_text
    report.doctor_diagnosis = payload.doctor_diagnosis
    report.status = ReportStatus.rejected.value
    db.commit()
    db.refresh(report)
    return report


@router.get("/{report_id}/pdf")
def download_pdf(report_id: int, _: User = Depends(get_current_user), db: Session = Depends(get_db)):
    report = _get_report_or_404(db, report_id)
    if not report.pdf_path:
        raise HTTPException(status_code=404, detail="PDF has not been generated yet")

    pdf_file = settings.base_dir / report.pdf_path
    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail="PDF file missing on disk")
    return FileResponse(pdf_file, media_type="application/pdf", filename=pdf_file.name)
