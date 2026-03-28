import streamlit as st
import numpy as np
import cv2
from PIL import Image
from model_inference import predict_plane, load_keras_model
from gemini_analysis import analyze_ultrasound

st.set_page_config(page_title="AI Fetal Ultrasound Analyzer", page_icon="🩺", layout="wide")

st.title("🩺 Fetal Ultrasound Hub")
st.markdown("Upload standard fetal ultrasound image to identify the biological plane, measure coordinate references, and generate AI-guided medical localization.")
st.write("")

# Orientation Meanings Dictionary
orientation_guide = {
    "Cephalic": "The baby's head is positioned downward.",
    "Breech": "The baby's feet or buttocks are positioned downward.",
    "Transverse": "The baby is lying horizontally across the uterus (sideways position).",
    "Longitudinal": "The baby is aligned vertically in the uterus (straight position).",
    "Unknown": "The baby's position could not be clearly determined."
}

uploaded_file = st.file_uploader("Upload Ultrasound Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Pre-Analysis Preview")
        st.image(image, caption="Uploaded Ultrasound Image", use_container_width=True)

    with col2:
        st.markdown("### AI Engine Control")
        if st.button("🚀 Analyze Ultrasound Image", use_container_width=True):
            with st.spinner("Processing..."):
                try:
                    # 1. Model Prediction
                    plane, confidence, model_part = predict_plane(image_np)
                    
                    # 2. Gemini Analysis
                    image_bytes = uploaded_file.getvalue()
                    result = analyze_ultrasound(image_bytes, plane, model_part)

                    # Data Extraction
                    if "error" in result:
                        api_error = True
                    else:
                        api_error = False
                        orientation = result.get("orientation", "Unknown")
                        coords = result.get("coordinates", [0, 0, 0, 0])

                    # --- OUTPUT DISPLAY ---
                    st.success("✅ Analysis Complete!")
                    st.markdown("### 📊 Primary Diagnosis Results")
                    
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    metric_col1.metric(label="Biological Plane", value=plane)
                    metric_col2.metric(label="Detected Part", value=model_part)
                    metric_col3.metric(label="Confidence Score", value=f"{confidence:.2%}")

                    st.markdown("### 📍 Positional Tracking")
                    if api_error:
                        st.warning("⚠️ Gemini API is currently unavailable or quota exceeded. Medical Orientation and Coordinates could not be generated.")
                    else:
                        st.write(f"**Medical Orientation:** {orientation}")
                        st.write(f"**Calculated Coordinates:** `{coords}`")
                        st.info(f"💡 **Clinical Interpretation:** {orientation_guide.get(orientation, orientation_guide['Unknown'])}")

                    # Drawing Bounding Box with Rescaling
                    st.markdown("### 🖼️ AI Spatial Localization")
                    if not api_error and any(c > 0 for c in coords):
                        h, w, _ = image_np.shape
                        # Rescale from 0-1000 to actual image pixels
                        x1 = int(coords[0] * w / 1000)
                        y1 = int(coords[1] * h / 1000)
                        x2 = int(coords[2] * w / 1000)
                        y2 = int(coords[3] * h / 1000)

                        box_img = image_np.copy()
                        cv2.rectangle(box_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        st.image(box_img, caption="Green Box indicates localized detection region", use_container_width=True)
                    else:
                        st.warning("⚠️ AI could not confidently localize the bounding box coordinates on this scan.")
                except Exception as e:
                    st.error(f"Error: {e}")


