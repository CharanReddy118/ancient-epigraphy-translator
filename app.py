import streamlit as st
import requests
import base64
import io
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="Universal Epigraphy Translator",
    page_icon="📜",
    layout="wide"
)

st.title("📜 Universal Indian Epigraphy & Script Translator")
st.write("Decipher and translate ancient stone inscriptions, copper plates, and manuscripts directly into Modern Telugu and English.")

# 2. API Key Configuration (Checks Streamlit Secrets first, falls back to Sidebar input)
secret_key = ""
if "GEMINI_API_KEY" in st.secrets:
    secret_key = st.secrets["GEMINI_API_KEY"]

st.sidebar.header("🔑 API Configuration")
user_key_input = st.sidebar.text_input("Enter Gemini API Key (Optional)", type="password")

# Use manual input if typed, otherwise fall back to the system secret key
api_key = user_key_input.strip() if user_key_input.strip() else secret_key

if secret_key and not user_key_input:
    st.sidebar.success("⚡ System API Key active! Ready to translate.")
elif not api_key:
    st.sidebar.warning("⚠️ No API key found. Enter one above or configure Streamlit Secrets.")
    st.sidebar.markdown("[Get or manage your API Key](https://aistudio.google.com/app/apikey)")

# 3. Vision Translation Engine
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
        "gemini-3.8-flash",
        "gemini-3.1-pro-preview",
        "gemini-3.5-flash-lite"
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
                    status_box.text("✅ Translation completed!")
                    return candidates[0]['content']['parts'][0]['text']
            else:
                err_msg = res_json.get('error', {}).get('message', 'Rejected')
                last_error = f"{model_name}: {err_msg}"
                continue
        except Exception as e:
            last_error = f"{model_name} timed out or failed: {str(e)}"
            continue

    return f"❌ **Execution Failed.**\n\nDetails: {last_error}"

# 4. Main UI Layout
uploaded_file = st.file_uploader("Upload Image of Inscription, Copper Plate, or Manuscript", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Inscription Image")
        st.image(uploaded_file, caption="Uploaded Inscription Image", use_container_width=True)

    with col2:
        st.subheader("2. AI Epigraphic Translation")
        
        if not api_key:
            st.warning("👈 Please enter your Gemini API key in the sidebar to proceed.")
        else:
            if st.button("Decipher & Translate Image", type="primary"):
                status_placeholder = st.empty()
                with st.spinner("Processing image..."):
                    result = translate_inscription_fast(uploaded_file, api_key, status_placeholder)
                    st.markdown(result)