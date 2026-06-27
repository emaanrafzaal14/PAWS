import streamlit as st
from PIL import Image

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="PAWS", page_icon="🐾")

# ---------------- TITLE ----------------
st.title("PAWS - Proactive Animal Welfare System 🐾")
st.markdown("AI-powered system for detecting animals needing assistance")

# ---------------- CAMERA INPUT ----------------
camera_image = st.camera_input("Point camera at the animal 📷")

# ---------------- PROCESS IMAGE ----------------
if camera_image:
    image = Image.open(camera_image)
    st.image(image, caption="Captured Image", use_container_width=True)

    st.write("🧠 Analyzing image...")

    # ---------------- TEMP AI PLACEHOLDER ----------------
    # (Replace this later with Edge Impulse API or exported model)
    prediction = "Unknown (Model Not Connected Yet)"

    st.success(f"Prediction: {prediction}")

    # ---------------- SAFE LOGIC ----------------
    if "injured" in prediction.lower():
        st.warning("⚠️ Animal may be injured. Contact local rescue immediately.")
    elif "stray" in prediction.lower():
        st.info("🐾 Stray detected. Provide safe help or report to NGO.")
    elif "healthy" in prediction.lower():
        st.success("✅ Animal appears healthy.")
    else:
        st.info("🧠 AI model is not connected yet. This is a placeholder output.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("Made with ❤️ for animal welfare")
