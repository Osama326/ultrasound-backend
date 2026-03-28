from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReportStatus(str, Enum):
    draft = "draft"
    pending_review = "pending_review"
    signed = "signed"
    rejected = "rejected"


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_age: Mapped[str] = mapped_column(String(50), nullable=False)
    patient_identifier: Mapped[str] = mapped_column(String(100), nullable=False)
    clinical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ai_report_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    doctor_diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=ReportStatus.draft.value, nullable=False)
    assigned_doctor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signed_by_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signature_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    doctor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    provider = relationship("User", back_populates="provider_reports", foreign_keys=[provider_id])
    doctor = relationship("User", back_populates="assigned_reports", foreign_keys=[doctor_id])
