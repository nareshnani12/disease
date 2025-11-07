import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import time

# ---------------- CONFIGURATION ----------------
st.set_page_config(page_title="🌿 AI Plant Disease Identifier", page_icon="🌱", layout="wide")

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# ---------------- THEME TOGGLE ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def apply_theme(theme):
    if theme == "light":
        bg, text, card, accent, border = "#f6fff8", "#1a202c", "#ffffff", "#2f855a", "#c6f6d5"
    else:
        bg, text, card, accent, border = "#0b1220", "#f0fff4", "#132a13", "#38a169", "#22543d"
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {bg};
            color: {text};
        }}
        .main-card {{
            background: {card};
            padding: 2rem;
            border-radius: 20px;
            border: 1px solid {border};
            box-shadow: 0px 8px 24px rgba(0,0,0,0.15);
        }}
        .btn-primary button {{
            background: {accent} !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
        }}
        h1, h2, h3, h4 {{ color: {accent}; }}
        </style>
    """, unsafe_allow_html=True)

# Sidebar theme switch
with st.sidebar:
    st.markdown("### 🌗 Appearance")
    dark_toggle = st.toggle("Dark Mode", value=(st.session_state.theme == "dark"))
    st.session_state.theme = "dark" if dark_toggle else "light"
    apply_theme(st.session_state.theme)

# ---------------- TITLE ----------------
st.markdown(
    """
    <div style='text-align:center; padding:1.5rem; border-radius:15px; background:rgba(56,178,172,0.1);'>
        <h1>🌿 AI-Based Plant Disease Identification System</h1>
        <p>A camera in every hand can now protect every plant!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- SESSION STATE ----------------
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

# ---------------- IMAGE INPUT ----------------
st.markdown("<div class='main-card'>", unsafe_allow_html=True)
st.header("📸 Upload or Capture Leaf Image")

uploaded_file = st.file_uploader(
    "Upload a clear image of the affected leaf",
    type=["jpg", "jpeg", "png"],
    key=f"uploader_{st.session_state.uploader_key}",
)

if st.button("📷 Take Photo"):
    st.session_state.camera_active = not st.session_state.camera_active

if st.session_state.camera_active:
    st.info("Click the **round capture button** below to take a photo.")
    camera_input = st.camera_input("Capture image here")
    if camera_input is not None:
        uploaded_file = None
        st.session_state.uploaded_image = Image.open(camera_input)
        st.session_state.camera_active = False
else:
    camera_input = None

if uploaded_file is not None:
    st.session_state.uploaded_image = Image.open(uploaded_file)

# ---------------- IMAGE DISPLAY ----------------
if st.session_state.uploaded_image is not None:
    st.image(st.session_state.uploaded_image, caption="Uploaded Image", use_container_width=True)
    st.success("✅ Image loaded successfully")

    if st.button("🔍 Identify Disease & Get Analysis", key="analyze_btn"):
        with st.spinner("Analyzing the leaf... Please wait ⏳"):
            try:
                img_byte_arr = io.BytesIO()
                st.session_state.uploaded_image.save(img_byte_arr, format="PNG")
                img_bytes = img_byte_arr.getvalue()

                prompt = """
                You are an expert agricultural AI assistant.
                Analyze the given leaf image and identify:
                1. The plant name
                2. Disease Name
                3. Cause/Pathogen
                4. Symptoms
                5. Severity Level (Low/Medium/High)
                6. Precautions
                7. Treatments (organic & chemical)
                8. Impact on yield or quality
                9. Future preventive measures
                Provide a structured and visually clear response.
                """

                model = genai.GenerativeModel("gemini-2.0-flash")
                response = model.generate_content([
                    prompt,
                    {"mime_type": "image/png", "data": img_bytes}
                ])

                st.session_state.analysis_result = response.text
                st.subheader("🌾 Disease Detection & Analysis Report")
                st.markdown(f"<div class='main-card'>{st.session_state.analysis_result}</div>", unsafe_allow_html=True)

                st.download_button(
                    label="📥 Download Report",
                    data=st.session_state.analysis_result,
                    file_name="plant_disease_analysis.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"⚠️ Error: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RESET FUNCTION ----------------
def trigger_reset():
    st.session_state.reset_triggered = True

# Display Reset button
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
st.button("🔄 Reset", on_click=trigger_reset, type="primary")
st.markdown("</div>", unsafe_allow_html=True)

# Perform reset safely
if st.session_state.reset_triggered:
    time.sleep(0.2)
    uploader_key = st.session_state.get("uploader_key", 0) + 1
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["uploader_key"] = uploader_key
    st.rerun()

# ---------------- FOOTER ----------------
st.markdown(
    """
    <hr>
    <div style='text-align:center; opacity:0.8;'>
        🌿 Built with ❤️ for Farmers | Powered by Techbusters</b>
    </div>
    """,
    unsafe_allow_html=True,
)
