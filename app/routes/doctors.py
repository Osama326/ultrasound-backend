from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.dependencies import get_current_user, require_doctor
from app.models.user import User, UserRole
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[UserResponse])
def list_doctors(search: str = "", db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    query = db.query(User).filter(User.role == UserRole.doctor)
    if search.strip():
        query = query.filter(User.full_name.ilike(f"%{search.strip()}%"))
    return query.order_by(User.full_name.asc()).all()


@router.post("/me/signature/upload", response_model=UserResponse)
def upload_signature(
    signature: UploadFile = File(...),
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    suffix = Path(signature.filename or "signature.png").suffix or ".png"
    relative_path = Path("signatures") / f"doctor_{doctor.id}_{uuid4().hex}{suffix}"
    absolute_path = settings.upload_path / relative_path
    absolute_path.write_bytes(signature.file.read())

    doctor.signature_path = str(relative_path).replace("\\", "/")
    db.commit()
    db.refresh(doctor)
    return doctor


@router.post("/me/signature/draw", response_model=UserResponse)
def save_drawn_signature(
    image_data: str = Form(...),
    doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db),
):
    if "," in image_data:
        import base64

        _, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)
    else:
        raise HTTPException(status_code=400, detail="Expected base64 data URL")

    relative_path = Path("signatures") / f"doctor_{doctor.id}_{uuid4().hex}.png"
    absolute_path = settings.upload_path / relative_path
    absolute_path.write_bytes(image_bytes)

    doctor.signature_path = str(relative_path).replace("\\", "/")
    db.commit()
    db.refresh(doctor)
    return doctor
