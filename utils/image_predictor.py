from pathlib import Path
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
import streamlit as st

# =====================
# PROJECT PATH
# =====================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "fmd_efficientnet_model.keras"

# =====================
# LOAD IMAGE MODEL
# =====================

@st.cache_resource
def load_image_model():
    print("Before loading image model...")
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
    return model
# =====================
# IMAGE PREDICTION
# =====================

def predict_image(uploaded_file):
    image_model = load_image_model()

    img = image.load_img(
        uploaded_file,
        target_size=(224, 224)
    )

    img_array = image.img_to_array(img)

    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    prediction = image_model.predict(
        img_array,
        verbose=0
    )

    prob = prediction[0][0]

    # prob قريبة من 0 = مريض (FMD)
    # prob قريبة من 1 = سليم (Healthy)
    fmd_probability = 1 - prob  # ← احتمال الإصابة بـ FMD

    if prob < 0.5:
        label = "FMD (Diseased)"
        confidence = fmd_probability * 100
    else:
        label = "Healthy"
        confidence = prob * 100

    return label, confidence, fmd_probability
