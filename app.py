
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
# 2. HERITAGE THEME
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #FCFBF8 !important;
        color: #293A32 !important;
        font-family: 'Inter', sans-serif;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        background-color: #252730 !important;
    }

    [data-testid="stSidebar"] * {
        color: #F7F5EF !important;
    }

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

    /* Upload container */
    [data-testid="stFileUploader"] {
        background: #F1F5EF !important;
        border: 1px solid #D7E2D5 !important;
        border-radius: 14px !important;
        padding: 12px !important;
    }

    /* Upload dropzone */
    [data-testid="stFileUploaderDropzone"] {
        background: #F8FAF6 !important;
        border: 2px dashed #A8BEA8 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small {
        color: #42594A !important;
    }

    /* Browse files button */
    [data-testid="stFileUploaderDropzone"] button {
        background: #24543A !important;
        color: #FFFFFF !important;
        border: 1px solid #24543A !important;
        border-radius: 7px !important;
    }

    [data-testid="stFileUploaderDropzone"] button * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background: #36724F !important;
    }

    /* Uploaded file details */
    [data-testid="stFileUploaderFile"] {
        background: #FFFFFF !important;
        border: 1px solid #DCE5D9 !important;
        border-radius: 8px !important;
    }

    [data-testid="stFileUploaderFile"] * {
        color: #344B3C !important;
    }

    /* Main action buttons */
    div.stButton > button {
        background: #24543A !important;
        color: #FFFFFF !important;
        border: 1px solid #24543A !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.2rem !important;
        font-weight: 600 !important;
    }

    div.stButton > button:hover {
        background: #36724F !important;
        border-color: #36724F !important;
    }

    [data-testid="stImage"] img {
        border-radius: 10px !important;
    }

    .discovery-placeholder {
        padding: 3rem 1.2rem;
        text-align: center;
        background: #FFFFFF;
        border: 1px solid #E1E7DE;
        border-radius: 12px;
    }

    .placeholder-title {
        font-size: 1.1rem;
        color: #344B3C !important;
    }

    .placeholder-text {
        font-size: 0.9rem;
        line-height: 1.7;
        color: #68796D !important;
    }

    [data-testid="stAlert"] {
        border-radius: 9px !important;
    }

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
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. GEMINI API KEY
# ==========================================
api_key = st.secrets.get("GEMINI_API_KEY", "").strip()


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
# 6. DISCOVER AVAILABLE GEMINI MODELS
# ==========================================
def get_available_models(key):
    """
    Fetch models available to this API key.
    Keep only models that support generateContent.
    """

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models"
    )

    available = []
    page_token = None

    try:
        # Handle pagination in the model list.
        for _ in range(10):
            params = {
                "key": key,
                "pageSize": 100
            }

            if page_token:
                params["pageToken"] = page_token

            response = requests.get(
                url,
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                try:
                    error_data = response.json()
                    message = error_data.get(
                        "error", {}
                    ).get("message", response.text)
                except ValueError:
                    message = response.text

                return [], str(message)

            data = response.json()

            for model in data.get("models", []):
                methods = model.get(
                    "supportedGenerationMethods", []
                )

                model_name = model.get("name", "")

                if (
                    model_name.startswith("models/gemini-")
                    and "generateContent" in methods
                ):
                    available.append(
                        model_name.replace("models/", "", 1)
                    )

            page_token = data.get("nextPageToken")

            if not page_token:
                break

        # Prefer fast general-purpose Gemini models.
        preferred_order = [
            "gemini-3.8-flash",
            "gemini-3-flash",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ]

        ordered = []

        for preferred in preferred_order:
            if preferred in available and preferred not in ordered:
                ordered.append(preferred)

        # Add any other eligible models returned by the API.
        for name in sorted(available):
            if name not in ordered:
                ordered.append(name)

        return ordered, None

    except requests.RequestException as e:
        return [], f"Could not contact Gemini API: {str(e)}"

    except (ValueError, TypeError) as e:
        return [], f"Could not read model list: {str(e)}"


# ==========================================
# 7. INSCRIPTION TRANSLATION ENGINE
# ==========================================
def translate_inscription(image_file, key, status_box):

    if not key:
        return (
            "⚠️ **API key missing.** Add `GEMINI_API_KEY` "
            "to your Streamlit secrets."
        )

    # Discover models instead of relying on retired names.
    status_box.info("🔎 Checking available Gemini models...")

    models, model_error = get_available_models(key)

    if model_error:
        return (
            "❌ **Unable to retrieve available Gemini models.**\n\n"
            f"**Details:** {model_error}\n\n"
            "Check that your API key is valid and that the Gemini "
            "API is enabled for your project."
        )

    if not models:
        return (
            "❌ **No compatible Gemini models found.**\n\n"
            "Your API key did not return any models supporting "
            "`generateContent`. Check your API key, project access, "
            "and available models."
        )

    # Prepare image.
    try:
        image_file.seek(0)

        with Image.open(image_file) as original:
            image = original.convert("RGB")

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=90)

        image_b64 = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

    except Exception as e:
        return f"❌ **Image processing error:** {str(e)}"

    prompt = """
    You are an experienced Indian epigraphist, historian, and linguist.

    Analyze the attached photograph of an ancient Indian inscription.

    Tasks:
    1. Identify the script and language, if possible.
    2. Transcribe characters that are genuinely readable.
    3. Explain the historical context, possible dynasty, ruler,
       period and purpose only when supported by evidence.
    4. Translate the readable content into modern Telugu.
    5. Translate the readable content into modern English.
    6. Mark damaged, uncertain or illegible passages clearly.
    7. Never invent missing text or claim a historical fact without
       sufficient evidence. Separate confirmed details from guesses.

    Use this Markdown format:

    ### 📜 Historical Context
    Explain the likely historical setting and confidence level.

    ### 🔤 Script and Transcription
    Identify the script and transcribe the readable text.

    ### 🇮🇳 Modern Telugu Translation (ఆధునిక తెలుగు భావం)
    Give the Telugu translation. Clearly mark uncertain passages.

    ### 🇬🇧 Modern English Translation
    Give the English translation.

    ### 📝 Notes and Uncertainties
    Explain damage, unreadable characters and any limitations.
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_b64
                        }
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4096
        }
    }

    last_error = ""

    # Try eligible models until one successfully responds.
    for model_name in models:
        status_box.info(
            f"🔎 Analyzing inscription with {model_name}..."
        )

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model_name}:generateContent"
        )

        try:
            response = requests.post(
                url,
                params={"key": key},
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120
            )

            try:
                data = response.json()
            except ValueError:
                last_error = (
                    f"{model_name}: API returned an invalid response."
                )
                continue

            if response.status_code == 200:
                candidates = data.get("candidates", [])

                if candidates:
                    parts = candidates[0].get(
                        "content", {}
                    ).get("parts", [])

                    result = "\n\n".join(
                        part["text"]
                        for part in parts
                        if "text" in part
                    )

                    if result.strip():
                        status_box.success(
                            f"✅ Analysis completed using {model_name}."
                        )
                        return result

                feedback = data.get("promptFeedback", {})
                reason = feedback.get(
                    "blockReason", "No text returned"
                )

                last_error = f"{model_name}: {reason}"
                continue

            error_data = data.get("error", {})
            error_code = error_data.get("code", response.status_code)
            error_message = error_data.get(
                "message", "Unknown API error"
            )
            error_status = error_data.get("status", "")

            last_error = (
                f"{model_name}: HTTP {error_code} - {error_message}"
            )

            # These errors are usually not fixed by switching models.
            if error_code in (400, 401, 403):
                status_box.error(
                    "Gemini rejected the request. Checking the error..."
                )

                # Continue only for model-specific incompatibility.
                lower_message = error_message.lower()

                model_issue = (
                    "not found" in lower_message
                    or "not supported" in lower_message
                    or "unsupported" in lower_message
                )

                if model_issue:
                    continue

                return (
                    "❌ **Gemini API rejected the request.**\n\n"
                    f"**Details:** {last_error}\n\n"
                    "Check your API key, permissions, image request, "
                    "and API configuration."
                )

            # Quota/rate-limit errors generally won't improve by
            # repeatedly switching models.
            if error_code == 429 or error_status == "RESOURCE_EXHAUSTED":
                return (
                    "⚠️ **Gemini API quota or rate limit reached.**\n\n"
                    f"**Details:** {last_error}\n\n"
                    "Check your Gemini API usage and quota, then retry."
                )

            # Server-side errors may be transient; try another model.
            continue

        except requests.Timeout:
            last_error = f"{model_name}: Request timed out."

        except requests.RequestException as e:
            last_error = f"{model_name}: Network error: {str(e)}"

        except Exception as e:
            last_error = f"{model_name}: {str(e)}"

    return (
        "❌ **Translation failed.**\n\n"
        f"**Last error:** {last_error}\n\n"
        "The API returned compatible model names, but none completed "
        "the request. Check model access, quota, and API status."
    )


# ==========================================
# 8. MAIN WORKSPACE
# ==========================================
st.markdown("---")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 📤 Upload an inscription")

    st.caption(
        "Choose a clear photograph of a temple inscription or manuscript."
    )

    uploaded_file = st.file_uploader(
        "Upload an inscription image",
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

    if uploaded_file is None:
        st.markdown(
            """
            <div class="discovery-placeholder">
                <p class="placeholder-title">
                    Your translation will appear here.
                </p>
                <p class="placeholder-text">
                    Upload an inscription to discover its historical
                    context, Telugu meaning and English translation
                    using multimodal AI.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif not api_key:
        st.error(
            "⚠️ `GEMINI_API_KEY` is missing from Streamlit secrets."
        )

    else:
        if st.button(
            "Begin translation ➜",
            type="primary",
            use_container_width=True
        ):
            status_placeholder = st.empty()

            with st.spinner(
                "Analyzing the inscription and interpreting its text..."
            ):
                result = translate_inscription(
                    uploaded_file,
                    api_key,
                    status_placeholder
                )

            st.markdown("---")
            st.markdown(result)


# ==========================================
# 9. FOOTER
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
