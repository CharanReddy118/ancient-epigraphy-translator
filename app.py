import streamlit as st
import requests
import base64
import io
from PIL import Image

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Heritage Inscription Archive",
    page_icon="📜",
    layout="wide"
)

# ==========================================
# 2. CUSTOM HERITAGE THEME
# ==========================================
st.markdown("""
<style>
    /* Main application */
    .stApp {
        background-color: #FCFBF8 !important;
        color: #293A32 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit default elements */
    #MainMenu,
    footer,
    header {
        visibility: hidden;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #252730 !important;
    }

    [data-testid="stSidebar"] * {
        color: #F7F5EF !important;
    }

    /* Hero section */
    .hero-tag {
        text-align: center;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.22rem;
        color: #92774D !important;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }

    .hero-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1B3B2B !important;
        margin-bottom: 0.5rem;
        font-family: Georgia, serif;
    }

    .hero-subtitle {
        text-align: center;
        font-size: 1.05rem;
        color: #63736A !important;
        margin: 0 auto 2.5rem auto;
        max-width: 850px;
        line-height: 1.8;
    }

    h1, h2, h3, h4 {
        color: #263C31 !important;
    }

    /* ==========================================
       FILE UPLOADER - LIGHT HERITAGE DESIGN
       ========================================== */

    /* Outer uploader container */
    [data-testid="stFileUploader"] {
        background: #F1F5EF !important;
        background-color: #F1F5EF !important;
        border: 1px solid #D7E2D5 !important;
        border-radius: 14px !important;
        padding: 12px !important;
    }

    /* Target uploader dropzone */
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"],
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section > div {
        background: #F8FAF6 !important;
        background-color: #F8FAF6 !important;
        border: 2px dashed #A8BEA8 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    /* Override dark backgrounds on uploader descendants */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section > div,
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"] {
        color: #344B3C !important;
    }

    /* Drag-and-drop instructions */
    [data-testid="stFileUploader"] section p,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section small,
    [data-testid="stFileUploader"] [data-testid="stFileUploadDropzoneInstructions"],
    [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] span,
    [data-testid="stFileUploadDropzone"] small {
        color: #42594A !important;
    }

    /* Upload button */
    [data-testid="stFileUploader"] section button,
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploadDropzone"] button {
        background: #24543A !important;
        background-color: #24543A !important;
        color: #FFFFFF !important;
        border: 1px solid #24543A !important;
        border-radius: 7px !important;
        font-weight: 600 !important;
        padding: 0.45rem 1.2rem !important;
        box-shadow: none !important;
        opacity: 1 !important;
    }

    /* Button label */
    [data-testid="stFileUploader"] section button *,
    [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stFileUploadDropzone"] button * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        opacity: 1 !important;
    }

    /* Upload icon */
    [data-testid="stFileUploader"] section button svg,
    [data-testid="stFileUploadDropzone"] button svg,
    [data-testid="stFileUploadDropzone"] button svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }

    /* Button hover */
    [data-testid="stFileUploader"] section button:hover,
    [data-testid="stFileUploaderDropzone"] button:hover,
    [data-testid="stFileUploadDropzone"] button:hover {
        background: #36724F !important;
        background-color: #36724F !important;
        border-color: #36724F !important;
    }

    /* Dropzone hover */
    [data-testid="stFileUploader"] section:hover,
    [data-testid="stFileUploadDropzone"]:hover {
        background: #EDF4EA !important;
        background-color: #EDF4EA !important;
        border-color: #527B5D !important;
    }

    /* Uploaded file card */
    [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #DCE5D9 !important;
        border-radius: 8px !important;
    }

    [data-testid="stFileUploaderFile"] * {
        color: #344B3C !important;
    }

    /* General buttons */
    div.stButton > button {
        background: #24543A !important;
        background-color: #24543A !important;
        color: #FFFFFF !important;
        border: 1px solid #24543A !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        background: #36724F !important;
        background-color: #36724F !important;
        border-color: #36724F !important;
        color: #FFFFFF !important;
    }

    div.stButton > button:focus {
        outline: 2px solid #A8BEA8 !important;
        outline-offset: 3px !important;
    }

    /* Image preview */
    [data-testid="stImage"] img {
        border-radius: 10px !important;
    }

    /* Translation placeholder */
    .discovery-placeholder {
        padding: 3rem 1.2rem;
        text-align: center;
        background: #FFFFFF;
        border: 1px solid #E1E7DE;
        border-radius: 12px;
        color: #68796D;
    }

    .placeholder-title {
        font-size: 1.1rem;
        color: #344B3C !important;
        margin-bottom: 0.6rem;
    }

    .placeholder-text {
        font-size: 0.9rem;
        line-height: 1.7;
        color: #68796D !important;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 9px !important;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 1.8rem;
        }

        .hero-tag {
            font-size: 0.7rem;
            letter-spacing: 0.12rem;
        }

        .hero-subtitle {
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }

        [data-testid="stFileUploader"] {
            padding: 8px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. GEMINI API KEY
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY", "")


# ==========================================
# 4. SIDEBAR
# ==========================================
st.sidebar.markdown("### 🏛️ Heritage Archive")
st.sidebar.markdown(
    "**Project:** Universal Epigraphy Translator"
)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Status")
st.sidebar.markdown(
    """
    - **Engine:** Gemini Vision API
    - **Timeout Limit:** 120s
    - **Status:** Online 🟢
    """
)


# ==========================================
# 5. HERO SECTION
# ==========================================
st.markdown(
    '<p class="hero-tag">PRESERVING THE STORIES OF OUR PAST</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="hero-title">Bring the past into focus.</p>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class="hero-subtitle">
        Start with a photograph of a temple inscription or manuscript
        to explore its historical text and English meaning.
    </p>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 6. TRANSLATION ENGINE
# ==========================================
def translate_inscription_fast(image_file, key, status_box):

    if not key:
        return (
            "⚠️ **Error:** API key is missing. "
            "Configure `GEMINI_API_KEY` in Streamlit secrets."
        )

    try:
        image_file.seek(0)

        with Image.open(image_file) as original_image:
            img = original_image.convert("RGB")
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=90)

        img_b64 = base64.b64encode(
            buffered.getvalue()
        ).decode("utf-8")

    except Exception as e:
        return f"❌ **Image Processing Error:** {str(e)}"

    prompt = """
    You are an experienced Indian epigraphist, historian, and linguist.

    Carefully analyze the attached photograph of an ancient inscription.

    Tasks:
    1. Identify the script and transcribe readable characters.
    2. Explain the historical context, dynasty, ruler, period, and
       purpose when supported by evidence.
    3. Translate the readable content into modern Telugu.
    4. Translate the readable content into modern English.
    5. Identify damaged, uncertain, or illegible portions.
    6. Never invent unreadable words or unsupported historical facts.
       Clearly distinguish confirmed information from interpretations.

    Format your response in Markdown:

    ### 📜 Historical Context

    ### 🔤 Script Identification and Transcription

    ### 🇮🇳 Modern Telugu Translation (ఆధునిక తెలుగు భావం)

    ### 🇬🇧 Modern English Translation

    ### 📝 Notes and Uncertainties
    """

    # 1. EXACT PAYLOAD FORMAT (camelCase)
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": img_b64
                    }
                }
            ]
        }]
    }

    # 2. BULLETPROOF MODEL TAGS
    target_models = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest"
    ]

    last_error = ""

    for model_name in target_models:

        status_box.info(f"🔎 Analyzing inscription with {model_name}...")

        # 3. USE V1BETA WITH EXPLICIT URL PARAMS
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"

        try:
            # Removed params={"key": key} since it's already in the URL
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120
            )

            try:
                res_json = response.json()
            except ValueError:
                last_error = (
                    f"{model_name}: Invalid response from the API."
                )
                continue

            if response.status_code == 200:
                candidates = res_json.get("candidates", [])

                if candidates:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])

                    text_parts = [
                        part["text"]
                        for part in parts
                        if "text" in part
                    ]

                    if text_parts:
                        status_box.success(
                            "✅ Inscription analysis completed."
                        )
                        return "\n\n".join(text_parts)

                last_error = (
                    f"{model_name}: No readable translation returned."
                )

            else:
                error_message = res_json.get(
                    "error", {}
                ).get("message", "Unknown API error")

                last_error = f"{model_name}: {error_message}"

        except requests.Timeout:
            last_error = f"{model_name}: Request timed out."

        except requests.RequestException as e:
            last_error = f"{model_name}: Network error: {str(e)}"

        except Exception as e:
            last_error = f"{model_name}: {str(e)}"

    return (
        "❌ **Translation failed.**\n\n"
        f"**Details:** {last_error}\n\n"
        "Check your API key, model availability, quota, and network."
    )


# ==========================================
# 7. MAIN WORKSPACE
# ==========================================
st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 📤 Upload an inscription")

    st.caption(
        "Choose a clear photograph of a temple inscription or manuscript."
    )

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
        help="Supported formats: PNG, JPG and JPEG.",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="Selected inscription",
            use_container_width=True
        )

        st.caption(
            f"File: {uploaded_file.name} · "
            f"{uploaded_file.size / 1024:.1f} KB"
        )


with col2:
    st.markdown("### 🔍 Your Discovery")

    if uploaded_file is not None:

        if not api_key:
            st.error(
                "⚠️ API key not configured. "
                "Add GEMINI_API_KEY to your Streamlit secrets."
            )

        elif st.button(
            "Begin translation ➜",
            type="primary",
            use_container_width=True
        ):
            status_placeholder = st.empty()

            with st.spinner(
                "Analyzing the inscription and interpreting its text..."
            ):
                result = translate_inscription_fast(
                    uploaded_file,
                    api_key,
                    status_placeholder
                )

            st.markdown("---")
            st.markdown(result)

    else:
        st.markdown(
            """
            <div class="discovery-placeholder">
                <p class="placeholder-title">
                    Your translation will appear here.
                </p>
                <p class="placeholder-text">
                    Upload an inscription to explore its historical
                    context, Telugu meaning, and English translation
                    using AI.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==========================================
# 8. FOOTER
# ==========================================
st.markdown("---")

st.markdown(
    """
    <p style="
        text-align: center;
        color: #829087;
        font-size: 0.85rem;
        padding: 8px 0;
    ">
        🏛️ Heritage Inscription Archive ·
        Preserving cultural history through technology
    </p>
    """,
    unsafe_allow_html=True
)