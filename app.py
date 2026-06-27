import streamlit as st
from PIL import Image
import os

# ---------------- SETUP ----------------
st.set_page_config(page_title="PAWS", page_icon="🐾")

st.title("PAWS - Proactive Animal Welfare System 🐾")
st.markdown("AI-powered animal welfare detection system using Edge Impulse")

# ---------------- CAMERA ----------------
camera_image = st.camera_input("Capture an animal image 📷")

# ---------------- PROCESS ----------------
if camera_image:
    image_path = "temp.jpg"
    
    # Save image from Streamlit
    with open(image_path, "wb") as f:
        f.write(camera_image.getbuffer())

    st.image(image_path, caption="Captured Image")

    st.write("🧠 Running Edge Impulse model...")

    # ---------------- RUN EDGE IMPULSE ----------------
    # IMPORTANT: your .eim must be set up in the same environment
    os.system(f"edge-impulse-linux-runner --image {image_path} > result.txt")

    # ---------------- READ OUTPUT ----------------
    try:
        with open("result.txt", "r") as f:
            result = f.read()

        st.success("Prediction Result:")
        st.text(result)

        # ---------------- SIMPLE ADVICE LAYER ----------------
        if "injured" in result.lower():
            st.warning("⚠️ Animal may be injured. Contact local animal rescue immediately.")
        elif "stray" in result.lower():
            st.info("🐾 Stray detected. Provide safe help or report to authorities.")
        else:
            st.success("✅ Animal appears healthy.")

    except:
        st.error("Model failed to run. Check Edge Impulse setup.")
st.write(result)
