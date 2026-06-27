import streamlit as st
import numpy as np
import cv2
from PIL import Image
import tensorflow as tf  # Stable TensorFlow engine for Streamlit Cloud
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime

# Official project submission title for NUST AI Course
st.title("PAWS - Proactive Animal Welfare System")

# ==========================================
# CONFIGURATION - ADJUST THESE VALUES!
# ==========================================
MODEL_PATH = "model.tflite"

# Mapping your classes exactly as Trained in Edge Impulse
# Index 0 and 1 must match the alphabetical order in Edge Impulse (e.g., "Injured", "Uninjured")
LABELS = ["Injured", "Uninjured"] 

# Email configurations (Using Gmail App Passwords)
SENDER_EMAIL = "your_course_email@gmail.com"  # <-- Change to your Gmail
SENDER_PASSWORD = "your_16_digit_app_password" # <-- Change to your 16-character App Password
RECEIVER_EMAIL = "emergency_contact@gmail.com"  # <-- Change to who gets the alerts
CAMERA_LOCATION = "NUST Campus, Islamabad"

# ==========================================
# CORE FUNCTION: EMAIL NOTIFICATION SYSTEM
# ==========================================
def send_injury_alert(image_bytes, label, confidence):
    try:
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

        # Attach the captured camera snapshot
        img_attachment = MIMEImage(image_bytes)
        img_attachment.add_header('Content-Disposition', 'attachment', filename="injured_animal.jpg")
        msg.attach(img_attachment)

        # Connect to Gmail Security Server
        server = smtplib.SMTP('://gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email system failed to broadcast: {e}")
        return False

# ==========================================
# CORE FUNCTION: MODEL LOADING & PREDICT
# ==========================================
@st.cache_resource
def load_tflite_model(path):
    # This loads the brains of your Edge Impulse file into Streamlit Cloud memory
    interpreter = tf.lite.Interpreter(model_path=path)
    interpreter.allocate_tensors()
    return interpreter

try:
    interpreter = load_tflite_model(MODEL_PATH)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Safely extract height and width from the standard 4D tensor shape [1, height, width, 3]
    expected_height = input_details[0]['shape'][1]
    expected_width = input_details[0]['shape'][2]

    # Camera feed input UI block
    img_file = st.camera_input("Point camera at the animal")

    if img_file is not None:
        # Save raw bytes for email attachment before processing
        raw_bytes = img_file.getvalue()
        
        image = Image.open(img_file).convert("RGB")
        img_array = np.array(image)
        
        # Mirroring Edge Impulse DSP sizing and normalization
        resized_img = cv2.resize(img_array, (expected_width, expected_height))
        normalized_img = resized_img.astype(np.float32) / 255.0
        input_data = np.expand_dims(normalized_img, axis=0)

        if st.button("Analyze Scan"):
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            
            output_data = interpreter.get_tensor(output_details[0]['index'])[0]
            max_idx = np.argmax(output_data)
            predicted_label = LABELS[max_idx]
            confidence_score = output_data[max_idx] * 100

            st.subheader("Analysis Results:")
            if predicted_label == "Injured":
                st.error(f"⚠️ {predicted_label} Cat Detected! ({confidence_score:.2f}% Confidence)")
                st.warning("Initiating emergency protocols... Dispatching emails.")
                
                with st.spinner("Broadcasting alert files to emergency services..."):
                    success = send_injury_alert(raw_bytes, predicted_label, confidence_score)
                    if success:
                        st.success("📩 Alerts successfully broadcasted with timestamp and location details!")
            else:
                st.success(f"✅ {predicted_label} Cat Detected ({confidence_score:.2f}% Confidence). No immediate threat found.")

except Exception as e:
    st.error(f"Pipeline Configuration Error: {e}")
