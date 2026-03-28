import tensorflow as tf
import numpy as np
import cv2

import streamlit as st

@st.cache_resource
def load_keras_model():
    return tf.keras.models.load_model("efficientnet_b2_ultrasound.h5")

classes = [
    "AC_PLANE",
    "BPD_PLANE",
    "FL_PLANE",
    "NO_PLANE"
]

# Mapping detected planes to specific body parts for context
part_map = {
    "AC_PLANE": "Abdomen",
    "BPD_PLANE": "Head",
    "FL_PLANE": "Femur",
    "NO_PLANE": "Unknown"
}

def predict_plane(image):
    """
    Preprocesses the image and predicts the ultrasound plane.
    Returns: (str) Plane Name, (float) Confidence, (str) Body Part
    """
    # Load the cached model
    model = load_keras_model()
    
    # Preprocess for EfficientNet-B2
    img = cv2.resize(image, (224, 224))
    # Note: efficientnet.preprocess_input is identity. 
    # The model handles rescaling internally, so we don't divide by 255.
    img = np.expand_dims(img, 0)

    # Prediction
    preds = model.predict(img)
    class_id = np.argmax(preds)

    plane = classes[class_id]
    confidence = float(np.max(preds))
    detected_part = part_map.get(plane, "Unknown")

    return plane, confidence, detected_part