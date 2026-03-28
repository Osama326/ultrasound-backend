from functools import lru_cache
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parents[2] / "vendor" / "Fetal_Ultrasound-main"
MODEL_PATH = MODEL_DIR / "efficientnet_b2_ultrasound.h5"
LAST_AI_ERROR = None

CLASSES = [
    "AC_PLANE",
    "BPD_PLANE",
    "FL_PLANE",
    "NO_PLANE",
]

PART_MAP = {
    "AC_PLANE": "Abdomen",
    "BPD_PLANE": "Head",
    "FL_PLANE": "Femur",
    "NO_PLANE": "Unknown",
}

PLANE_SUMMARIES = {
    "AC_PLANE": "The uploaded image is most consistent with an abdominal circumference view.",
    "BPD_PLANE": "The uploaded image is most consistent with a biparietal diameter or fetal head view.",
    "FL_PLANE": "The uploaded image is most consistent with a femur length view.",
    "NO_PLANE": "The model could not confidently match the image to a supported standard plane.",
}

PLANE_RECOMMENDATIONS = {
    "AC_PLANE": "Correlate with fetal growth measurements and confirm interpretation during formal review.",
    "BPD_PLANE": "Correlate with fetal head measurements and confirm interpretation during formal review.",
    "FL_PLANE": "Correlate with fetal long-bone measurements and confirm interpretation during formal review.",
    "NO_PLANE": "Repeat image acquisition or review image quality if a standard fetal plane is expected.",
}


@lru_cache(maxsize=1)
def _load_model():
    global LAST_AI_ERROR
    try:
        import tensorflow as tf
    except Exception as exc:
        LAST_AI_ERROR = f"TensorFlow import failed: {exc}"
        return None

    if not MODEL_PATH.exists():
        LAST_AI_ERROR = f"Model file missing: {MODEL_PATH}"
        return None

    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        LAST_AI_ERROR = None
        return model
    except Exception as exc:
        LAST_AI_ERROR = f"Model load failed: {exc}"
        return None


def _predict_plane(image_path: Path):
    model = _load_model()
    if model is None:
        return None

    try:
        import numpy as np
        from PIL import Image
    except Exception as exc:
        global LAST_AI_ERROR
        LAST_AI_ERROR = f"Image preprocessing import failed: {exc}"
        return None

    try:
        image = Image.open(image_path).convert("RGB").resize((224, 224))
        image_np = np.array(image)
        batch = np.expand_dims(image_np, 0)
        predictions = model.predict(batch, verbose=0)

        class_index = int(predictions.argmax())
        plane = CLASSES[class_index]
        confidence = float(predictions[0][class_index])
        detected_part = PART_MAP.get(plane, "Unknown")
        LAST_AI_ERROR = None
        return plane, confidence, detected_part
    except Exception as exc:
        LAST_AI_ERROR = f"Prediction failed: {exc}"
        return None


def _build_report_text(patient_name: str, image_path: Path, prediction):
    if not prediction:
        diagnostic_line = f"Diagnostic detail: {LAST_AI_ERROR}\n" if LAST_AI_ERROR else ""
        return (
            f"Jeejal AI Report for {patient_name}\n\n"
            f"Source image: {image_path.name}\n"
            "AI analysis fallback: the backend is ready for real model inference, but the AI runtime is not installed yet.\n"
            f"{diagnostic_line}"
            "To enable the real fetal ultrasound model, run this backend on a TensorFlow-supported Python version and install the AI requirements.\n"
            "Current status: report created successfully, awaiting full AI model activation."
        )

    plane, confidence, detected_part = prediction
    plane_label = plane.replace("_", " ").title()
    summary = PLANE_SUMMARIES.get(plane, "The image was processed successfully by the AI model.")
    recommendation = PLANE_RECOMMENDATIONS.get(
        plane,
        "Please review the image alongside the full clinical context before final sign-off.",
    )
    confidence_label = _classify_confidence(confidence)

    return (
        f"Jeejal AI Report\n\n"
        f"Patient: {patient_name}\n"
        f"Source image: {image_path.name}\n\n"
        "AI Findings:\n"
        f"- Predicted plane: {plane_label}\n"
        f"- Predicted anatomical target: {detected_part}\n"
        f"- Confidence score: {confidence:.2%} ({confidence_label})\n\n"
        "Preliminary Interpretation:\n"
        f"{summary}\n\n"
        "Clinical Recommendation:\n"
        f"{recommendation}\n\n"
        "Important Note:\n"
        "This is an AI-assisted preliminary report and must be reviewed, edited if needed, and signed by a qualified doctor before clinical use."
    )


def generate_ai_report(image_path: Path, patient_name: str) -> dict:
    prediction = _predict_plane(image_path)
    return {
        "report_text": _build_report_text(patient_name, image_path, prediction),
    }


def _classify_confidence(confidence: float) -> str:
    if confidence >= 0.9:
        return "high confidence"
    if confidence >= 0.7:
        return "moderate confidence"
    return "low confidence"
