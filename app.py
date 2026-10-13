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

# 2. Sidebar Configuration
st.sidebar.header("🔑 API Configuration")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.markdown("[Get or manage your API Key](https://aistudio.google.com/app/apikey)")

# 3. Vision Translation Engine with Smart Fallback
def translate_inscription_with_fallback(image_file, key):
    if not key:
        return "⚠️ **Error:** Please enter your Gemini API key in the sidebar."

    # Convert uploaded image to RGB Base64
    try:
        img = Image.open(image_file).convert('RGB')
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=95)
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

    # Fetch available models directly from Google API
    candidate_models = []
    models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        res = requests.get(models_url, timeout=5)
        if res.status_code == 200:
            for m in res.json().get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    name = m.get('name', '').replace('models/', '')
                    # Filter out known deprecated models
                    if 'gemini' in name and '2.5' not in name:
                        candidate_models.append(name)
    except Exception:
        pass

    # Standard model fallbacks sorted by reliability on free/tier quotas
    default_order = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest"
    ]

    # Combine fetched models with fallbacks preserving priority
    all_models = []
    for m in candidate_models + default_order:
        if m not in all_models:
            all_models.append(m)

    # Waterfall execution: tries models sequentially until one succeeds
    last_error = ""
    for model_name in all_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
            res_json = response.json()

            if response.status_code == 200:
                candidates = res_json.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    # Successful response retrieved
                    return res_json['candidates'][0]['content']['parts'][0]['text']
            else:
                err_msg = res_json.get('error', {}).get('message', str(res_json))
                last_error = f"Model `{model_name}` returned error ({response.status_code}): {err_msg}"
                continue
        except Exception as e:
            last_error = f"Request error on `{model_name}`: {str(e)}"
            continue

    return f"❌ **All API Models Failed.**\n\nLast Error: {last_error}\n\nPlease check your API key at https://aistudio.google.com/app/apikey"

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
                with st.spinner("Analyzing stone and finding an active model..."):
                    result = translate_inscription_with_fallback(uploaded_file, api_key)
                    st.markdown(result)