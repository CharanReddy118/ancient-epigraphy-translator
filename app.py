import streamlit as st
import requests
import base64
import io
from PIL import Image

# 1. Page Configuration
st.set_page_config(
    page_title="Heritage Inscription Archive",
    page_icon="📜",
    layout="wide"
)

# Custom Heritage Theme CSS (Fixing card and uploader visibility)
st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #fcfbfa;
            color: #2c3531;
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Typography */
        .hero-tag {
            text-align: center;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.2rem;
            color: #8c7853;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .hero-title {
            text-align: center;
            font-size: 2.8rem;
            font-weight: 700;
            color: #1b3b2b;
            margin-bottom: 0.5rem;
            font-family: serif;
        }
        .hero-subtitle {
            text-align: center;
            font-size: 1.05rem;
            color: #5c6b63;
            margin-bottom: 2.5rem;
        }

        /* Custom Button Styling */
        div.stButton > button:first-child {
            background-color: #1b3b2b;
            color: white;
            border-radius: 4px;
            padding: 0.6rem 1.5rem;
            font-weight: 500;
            border: none;
            width: 100%;
        }
        div.stButton > button:first-child:hover {
            background-color: #2c5843;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# 2. Secure Secret Key Handling (Completely hidden from user)
api_key = ""
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]

# Minimalist sidebar
st.sidebar.markdown("### 🏛️ Heritage Archive")
st.sidebar.markdown("**Project:** Universal Epigraphy Translator")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Status")
st.sidebar.markdown("• **Engine:** Gemini Vision API\n• **Timeout Limit:** 120s\n• **Status:** Online 🟢")

# Header Section
st.markdown('<p class="hero-tag">PRESERVING THE STORIES OF OUR PAST</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-title">Bring the past into focus.</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Start with a photograph of a temple inscription or manuscript to explore its historical text and English meaning.</p>', unsafe_allow_html=True)

# 3. Vision Translation Engine Function
def translate_inscription_fast(image_file, key, status_box):
    if not key:
        return "⚠️ **Error:** System API Key is missing in Streamlit Cloud secrets."

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
        status_box.text("⚡ Processing artifact matrix...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        
        try:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
            res_json = response.json()

            if response.status_code == 200:
                candidates = res_json.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    status_box.text("✅ Decipherment completed successfully!")
                    return candidates[0]['content']['parts'][0]['text']
            else:
                err_msg = res_json.get('error', {}).get('message', 'Rejected')
                last_error = f"{model_name}: {err_msg}"
                continue
        except Exception as e:
            last_error = f"{model_name} timed out or failed: {str(e)}"
            continue

    return f"❌ **Execution Failed.**\n\nDetails: {last_error}"

# 4. Main Workspace Layout (Clean Two-Column Design)
st.markdown("---")
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 📤 Upload an inscription")
    uploaded_file = st.file_uploader("Choose a photo from your phone or computer", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Selected Artifact", use_container_width=True)
    else:
        st.markdown("""
            <div style="padding: 2.5rem 1rem; text-align: center; background-color: #ffffff; border: 2px dashed #d1d8d3; border-radius: 8px; color: #5c6b63;">
                <p style="font-size: 1rem; font-weight: 500; margin-bottom: 0.2rem;">Drop inscription photo here</p>
                <p style="font-size: 0.8rem; color: #8c9a92;">Supports PNG, JPG, JPEG</p>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 🔍 Your Discovery")
    
    if uploaded_file is not None:
        if not api_key:
            st.error("⚠️ System Error: GEMINI_API_KEY is not configured in Streamlit secrets.")
        else:
            if st.button("Begin translation ➔", type="primary"):
                status_placeholder = st.empty()
                with st.spinner("Analyzing stone matrix and script structures..."):
                    result = translate_inscription_fast(uploaded_file, api_key, status_placeholder)
                    st.markdown("---")
                    st.markdown(result)
    else:
        st.markdown("""
            <div style="padding: 3.2rem 1rem; text-align: center; background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; color: #8c9a92;">
                <p style="font-size: 1.1rem; margin-bottom: 0.5rem; color: #374151;">Your translation will appear here.</p>
                <p style="font-size: 0.85rem;">This step processes inscription pixels using multimodal AI.</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<br><hr><p style='text-align: center; color: #8c9a92; font-size: 0.8rem;'>Heritage Inscription Archive • A project to preserve cultural history</p>", unsafe_allow_html=True)