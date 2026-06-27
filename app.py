import streamlit as st
from PIL import Image

# ---------------- UI TITLE ----------------
st.title("PAWS - Proactive Animal Welfare System 🐾")

st.markdown(
    "<p style='color:#7A2E2E; font-size:18px;'>AI for compassionate animal care and quick detection of animals needing help</p>",
    unsafe_allow_html=True
)

st.markdown("### Upload an image to detect whether an animal needs attention.")

# ---------------- IMAGE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

# ---------------- MAIN LOGIC ----------------
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    st.write("🧠 Analyzing image using AI model...")

    # ---------------- PLACEHOLDER PREDICTION ----------------
    # (We will connect Edge Impulse model later)
    prediction = "Stray (Demo Output)"

    st.success(f"Prediction: {prediction}")

    # ---------------- ADVICE SECTION ----------------
    if "Injured" in prediction:
        st.info("⚠️ The animal may be injured. Contact local animal rescue immediately and avoid direct handling.")
    elif "Stray" in prediction:
        st.info("🐾 The animal appears stray. Consider reporting to animal welfare services or providing safe food/water.")
    else:
        st.info("✅ The animal appears healthy. No immediate action required.")
