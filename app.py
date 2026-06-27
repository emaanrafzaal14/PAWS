import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tflite_runtime.interpreter as tflite  # Native integration for your Edge Impulse file
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

# Official project branding
st.title("PAWS - Proactive Animal Welfare System")

# ==========================================
# CONFIGURATION - LIVE DEMO SETTINGS
# ==========================================
MODEL_PATH = "model.tflite"
LABELS = ["Injured", "Uninjured"] 

# 🚨 PASTE YOUR NGO EMAIL DETAILS HERE
SENDER_EMAIL = "reham4strays@gmail.com"      
SENDER_PASSWORD = "ucht cbdi uxrq kwni" 
RECEIVER_EMAIL = "reham4strays@gmail.com"    
CAMERA_LOCATION = "NUST Campus, Islamabad"

# ==========================================
# CORE FUNCTION: REAL EMAIL DISPATCH SYSTEM
# ==========================================
def send_injury_alert(image_bytes, label, confidence):
    # No fallbacks. If this fails, it will bubble up the error to debug live.
    msg = MIMEMultipart()
    msg['Subject'] = f"🚨 URGENT: Injured Animal Spotted at {CAMERA_LOCATION}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    body = f"""
    Warning: An injured animal has been identified by the surveillance network.
    
    - Status: {label} Cat Detected
    - Confidence Level: {confidence:.2f}%
    - Time Flagged: {current_time}
    - Camera Location: {CAMERA_LOCATION}
    - Medical Attention Required: YES - IMMEDIATE ACTION
    
    Please check the attached snapshot for visual confirmation.
    """
    msg.attach(MIMEText(body, 'plain'))

    img_attachment = MIMEImage(image_bytes)
    img_attachment.add_header('Content-Disposition', 'attachment', filename="injured_animal.jpg")
    msg.attach(img_attachment)

    # CRITICAL FIX: Using Port 465 via SMTP_SSL to bypass Streamlit network blocks
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()
    return True

# ==========================================
# CORE FUNCTION: NATIVE MODEL RUNNER
# ==========================================
@st.cache_resource
def load_tflite_model(path):
    interpreter = tflite.Interpreter(model_path=path)
    interpreter.allocate_tensors()
    return interpreter

try:
    # Verifiably loads your actual uploaded model.tflite file from your repository
    interpreter = load_tflite_model(MODEL_PATH)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    expected_height = input_details['shape']
    expected_width = input_details['shape']

    # Native camera input widget
    img_file = st.camera_input("Point camera at the animal")

    # AUTOMATED TRIGGER: Executes immediately when "Take Photo" is clicked
    if img_file is not None:
        raw_bytes = img_file.getvalue()
        
        image = Image.open(img_file).convert("RGB")
        img_array = np.array(image)
        
        # Resizing pixels to match your exact Edge Impulse model properties
        resized_img = cv2.resize(img_array, (expected_width, expected_height))
        normalized_img = resized_img.astype(np.float32) / 255.0
        input_data = np.expand_dims(normalized_img, axis=0)

        with st.spinner("Processing image via Edge Impulse model..."):
            interpreter.set_tensor(input_details['index'], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details['index'])
            
            max_idx = np.argmax(output_data)
            predicted_label = LABELS[max_idx]
            confidence_score = output_data[max_idx] * 100

        st.subheader("Analysis Results:")
        if predicted_label == "Injured":
            st.error(f"⚠️ {predicted_label} Cat Detected! ({confidence_score:.2f}% Confidence)")
            st.warning("Initiating emergency protocols... Dispatching emails.")
            
            with st.spinner("Broadcasting alert files to emergency services..."):
                if send_injury_alert(raw_bytes, predicted_label, confidence_score):
                    st.success("📩 Alerts successfully broadcasted live! Check your inbox.")
        else:
            st.success(f"✅ {predicted_label} Cat Detected ({confidence_score:.2f}% Confidence). No immediate threat found.")

except Exception as e:
    st.error(f"Pipeline Configuration Error: {e}")
