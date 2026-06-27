import streamlit as st
from PIL import Image

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="PAWS", page_icon="🐾")

# ---------------- TITLE ----------------
st.title("PAWS - Proactive Animal Welfare System 🐾")

st.markdown(
    "<p style='color:#7A2E2E; font-size:18px;'>AI-powered system for detecting animals needing attention</p>",
    unsafe_allow_html=True
)

st.markdown("### Point your camera at an animal 📷")

# ---------------- CAMERA INPUT ----------------
camera_image = st.camera_input("Capture image")

# ---------------- PROCESS IMAGE ----------------
if camera_image:
    image = Image.open(camera_image)
    st.image(image, caption="Captured Image", use_container_width=True)

    st.write("🧠 Running AI model...")

    # ---------------- PLACEHOLDER MODEL OUTPUT ----------------
    # (Edge Impulse model will replace this later)
    prediction = "Stray (Demo Output)"

    st.success(f"Prediction: {prediction}")

    # ---------------- ADVICE SYSTEM ----------------
    if "Injured" in prediction:
        st.info("⚠️ The animal may be injured. Contact a local animal rescue immediately.")
    elif "Stray" in prediction:
        st.info("🐾 The animal appears stray. Provide safe help or report to authorities.")
    else:
        st.info("✅ The animal appears healthy. No immediate action required.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("Made with ❤️ for animal welfare")
