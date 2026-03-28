from datetime import datetime

from pydantic import BaseModel


class ReportCreateRequest(BaseModel):
    patient_name: str
    patient_age: str
    patient_identifier: str
    clinical_notes: str | None = None


class AssignDoctorRequest(BaseModel):
    doctor_id: int


class SignReportRequest(BaseModel):
    doctor_diagnosis: str | None = None
    report_text: str | None = None


class RejectAndEditRequest(BaseModel):
    doctor_diagnosis: str
    report_text: str | None = None


class ReportResponse(BaseModel):
    id: int
    patient_name: str
    patient_age: str
    patient_identifier: str
    clinical_notes: str | None = None
    image_path: str | None = None
    ai_report_text: str | None = None
    doctor_diagnosis: str | None = None
    status: str
    assigned_doctor_name: str | None = None
    signed_by_name: str | None = None
    signature_path: str | None = None
    pdf_path: str | None = None
    provider_id: int
    doctor_id: int | None = None
    created_at: datetime
    updated_at: datetime
    signed_at: datetime | None = None

    model_config = {"from_attributes": True}
