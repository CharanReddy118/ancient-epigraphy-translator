import streamlit as st
import requests
import base64
import io
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="Epigraphy & Script Translator Dashboard",
    page_icon="📜",
    layout="wide"
)

# Custom Dashboard Styling
st.markdown("""
    <style>
        .main-header { font-size: 2.2rem; font-weight: 700; color: #f3f4f6; margin-bottom: 0rem; }
        .sub-header { font-size: 1rem; color: #9ca3af; margin-bottom: 2rem; }
        .metric-card { background-color: #1f2937; padding: 1rem; border-radius: 0.5rem; border: 1px solid #374151; }
    </style>
""", unsafe_allow_html=True)

# 2. API Key Configuration
secret_key = ""
if "GEMINI_API_KEY" in st.secrets:
    secret_key = st.secrets["GEMINI_API_KEY"]

st.sidebar.header("🎛️ Workspace Control")
st.sidebar.markdown("Manage your epigraphic analysis workspace settings.")
user_key_input = st.sidebar.text_input("Gemini API Key (Optional)", type="password")

api_key = user_key_input.strip() if user_key_input.strip() else secret_key

if secret_key and not user_key_input:
    st.sidebar.success("⚡ System API Key Active")
elif not api_key:
    st.sidebar.warning("⚠️ No API Key Configured")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Stats")
st.sidebar.markdown("• **Engine:** Gemini Vision API\n• **Timeout Limit:** 120s\n• **Fallback:** Multi-Model Active\n• **Status:** Operational 🟢")

# Dashboard Title Banner
st.markdown('<p class="main-header">📜 Epigraphy & Script Translator Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced multimodal analysis workspace for ancient stone inscriptions, copper plates, and manuscripts.</p>', unsafe_allow_html=True)

# Top Dashboard Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Active Models", value="3-Tier Fallback", delta="Optimized")
with m2:
    st.metric(label="Processing Limit", value="120 Seconds", delta="Extended Timeout")
with m3:
    st.metric(label="Output Languages", value="Telugu & English", delta="Bilingual")
with m4:
    st.metric(label="Security Vault", value="Streamlit Secrets", delta="Secured 🔒")

st.markdown("---")

# 3. Vision Translation Engine Function
def translate_inscription_fast(image_file, key, status_box):
    if not key:
        return "⚠️ **Error:** No valid Gemini API key found."

    try:
        img = Image.open(image_file).convert('RGB')
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=90)
        img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        return f"❌ **Image Processing Error:** {str(e)}"

    prompt = """
    You are an elite Indian epigraphist, historian, and linguist. Look directly at the attached image of an ancient inscription.
    
    Task:
    1. Read the ancient script natively from the stone/surface.
    2. Identify the historical context (e.g., Dynasty, King, Era, Purpose of the inscription).
    3. Provide a clear, fluent translation in Modern Telugu.
    4. Provide a clear, fluent translation in Modern English.
    
    Format your response beautifully using Markdown:
    ### 📜 Historical Context
    (Your context here)
    
    ### 🇮🇳 Modern Telugu Translation (ఆధునిక తెలుగు భావం)
    (Your Telugu translation here)
    
    ### 🇬🇧 Modern English Translation
    (Your English translation here)
    """

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64
                    }
                }
            ]
        }]
    }

    target_models = [
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]

    last_error = ""
    for model_name in target_models:
        status_box.text(f"⚡ Connecting to model: {model_name}...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
            res_json = response.json()

            if response.status_code == 200:
                candidates = res_json.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    status_box.text("✅ Analysis completed successfully!")
                    return candidates[0]['content']['parts'][0]['text']
            else:
                err_msg = res_json.get('error', {}).get('message', 'Rejected')
                last_error = f"{model_name}: {err_msg}"
                continue
        except Exception as e:
            last_error = f"{model_name} timed out or failed: {str(e)}"
            continue

    return f"❌ **Execution Failed.**\n\nDetails: {last_error}"

# 4. Main Workspace Layout (Dashboard Split)
uploaded_file = st.file_uploader("📂 Upload Inscription Image (PNG, JPG, JPEG)", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 🖼️ Artifact Preview")
        st.image(uploaded_file, caption="Uploaded Artifact Matrix", use_container_width=True)

    with col2:
        st.markdown("### 🔍 Epigraphic Intelligence Workspace")
        
        if not api_key:
            st.warning("👈 Please enter your Gemini API key in the sidebar to run analysis.")
        else:
            if st.button("🚀 Decipher & Translate Artifact", type="primary", use_container_width=True):
                status_placeholder = st.empty()
                with st.spinner("Executing multimodal vision analysis..."):
                    result = translate_inscription_fast(uploaded_file, api_key, status_placeholder)
                    st.markdown("---")
                    st.markdown(result)
else:
    st.info("👆 Upload an inscription image above to initialize the analysis workspace.")