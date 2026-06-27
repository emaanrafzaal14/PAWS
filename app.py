import streamlit as st
import numpy as np
import cv2
from PIL import Image
import onnxruntime as ort  # Ultra-lightweight and stable for Streamlit Cloud
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
# To match the ONNX engine, ensure your downloaded file from Edge Impulse is .onnx format!
MODEL_PATH = "model.onnx"

# Mapping your classes exactly as Trained in Edge Impulse
LABELS = ["Injured", "Uninjured"] 

# Email configurations (Using Gmail App Passwords)
SENDER_EMAIL = "your_course_email@gmail.com"  
SENDER_PASSWORD = "your_16_digit_app_password" 
RECEIVER_EMAIL = "emergency_contact@gmail.com"  
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

        img_attachment = MIMEImage(image_bytes)
        img_attachment.add_header('Content-Disposition', 'attachment', filename="injured_animal.jpg")
        msg.attach(img_attachment)

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
def load_onnx_model(path):
    # This loads the lightweight ONNX runtime engine
    session = ort.InferenceSession(path)
    return session

try:
    session = load_onnx_model(MODEL_PATH)
    input_details = session.get_inputs()[0]
    output_details = session.get_outputs()[0]
    
    # Extract expected resolution dimensions from the model profile shape
    # Typically shape looks like [1, 3, 96, 96] or [1, 96, 96, 3] depending on compilation
    shape = input_details.shape
    
    # Intelligently find height and width whether channels are first or last
    if shape[1] == 3 or shape[1] == 1:
        expected_height, expected_width = shape[2], shape[3]
        channels_first = True
    else:
        expected_height, expected_width = shape[1], shape[2]
        channels_first = False

    # Camera feed input UI block
    img_file = st.camera_input("Point camera at the animal")

    if img_file is not None:
        raw_bytes = img_file.getvalue()
        
        image = Image.open(img_file).convert("RGB")
        img_array = np.array(image)
        
        # Mirroring Edge Impulse DSP sizing and normalization
        resized_img = cv2.resize(img_array, (expected_width, expected_height))
        normalized_img = resized_img.astype(np.float32) / 255.0
        
        if channels_first:
            # Reorder dimensions from [H, W, C] to [C, H, W] if your ONNX structure requires it
            normalized_img = np.transpose(normalized_img, (2, 0, 1))
            
        input_data = np.expand_dims(normalized_img, axis=0)

        if st.button("Analyze Scan"):
            # Run cloud inference using ONNX Runtime
            input_name = input_details.name
            output_data = session.run(None, {input_name: input_data})[0][0]
            
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
