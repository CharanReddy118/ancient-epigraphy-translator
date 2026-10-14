
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

    /* Upload area */
    [data-testid="stFileUploader"] {
        background: #F1F5EF !important;
        border: 1px solid #D7E2D5 !important;
        border-radius: 14px !important;
        padding: 12px !important;
    }

    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploadDropzone"] {
        background: #F8FAF6 !important;
        background-color: #F8FAF6 !important;
        border: 2px dashed #A8BEA8 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    [data-testid="stFileUploaderDropzone"] p,
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploadDropzone"] p,
    [data-testid="stFileUploadDropzone"] span {
        color: #42594A !important;
    }

    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploadDropzone"] button {
        background: #24543A !important;
        color: #FFFFFF !important;
        border: 1px solid #24543A !important;
        border-radius: 7px !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploaderDropzone"] button *,
    [data-testid="stFileUploadDropzone"] button * {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover,
    [data-testid="stFileUploadDropzone"] button:hover {
        background: #36724F !important;
    }

    [data-testid="stFileUploaderFile"] {
        background: #FFFFFF !important;
        border: 1px solid #DCE5D9 !important;
        border-radius: 8px !important;
    }

    [data-testid="stFileUploaderFile"] * {
        color: #344B3C !important;
    }

    /* Translation button */
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
# 3. API KEY
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
    - **Timeout Limit:** 120 seconds
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
# 6. GET MODELS AVAILABLE TO THIS API KEY
# ==========================================
def get_available_models(key):
    """
    Retrieve models available to this API key.
    Select only models supporting generateContent.
    """

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models"
    )

    available = []
    page_token = None

    try:
        # Follow pagination if the model list has multiple pages.
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
                    data = response.json()
                    message = data.get(
                        "error", {}
                    ).get("message", response.text)
                except ValueError:
                    message = response.text

                return [], (
                    f"HTTP {response.status_code}: {message}"
                )

            data = response.json()

            for model in data.get("models", []):
                model_name = model.get("name", "")
                short_name = model_name.removeprefix("models/")
                methods = model.get(
                    "supportedGenerationMethods", []
                )

                # Exclude special-purpose computer-use models.
                if (
                    short_name.startswith("gemini-")
                    and "generateContent" in methods
                    and "computer-use" not in short_name.lower()
                ):
                    available.append(short_name)

            page_token = data.get("nextPageToken")

            if not page_token:
                break

        # Try preferred general-purpose multimodal models first.
        preferred_order = [
            "gemini-3.5-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.6-flash",
            "gemini-3.8-flash",
            "gemini-3.1-flash-lite",
            "gemini-3-flash",
            "gemini-3-flash-preview",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
        ]

        ordered = []

        for preferred in preferred_order:
            if preferred in available and preferred not in ordered:
                ordered.append(preferred)

        # Include other eligible models reported by Google.
        for name in sorted(set(available)):
            if name not in ordered:
                ordered.append(name)

        if not ordered:
            return [], (
                "Google returned no Gemini models supporting "
                "generateContent for this API key."
            )

        return ordered, None

    except requests.RequestException as e:
        return [], f"Could not connect to Gemini API: {e}"

    except (ValueError, TypeError) as e:
        return [], f"Could not process the model list: {e}"


# ==========================================
# 7. TRANSLATION ENGINE
# ==========================================
def translate_inscription(image_file, key, status_box):

    if not key:
        return (
            "⚠️ **API key missing.** Add `GEMINI_API_KEY` "
            "to Streamlit secrets."
        )

    # Discover current model availability.
    status_box.info("🔎 Checking available Gemini models...")

    models, model_error = get_available_models(key)

    if model_error:
        return (
            "❌ **Could not retrieve Gemini models.**\n\n"
            f"**Details:** {model_error}\n\n"
            "Check your API key, project access and API configuration."
        )

    # Prepare image bytes.
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
        return f"❌ **Image processing error:** {e}"

    prompt = """
    You are an experienced Indian epigraphist, historian and linguist.

    Analyze the attached photograph of an ancient Indian inscription.

    Tasks:
    1. Identify the script and language if possible.
    2. Transcribe only characters that can reasonably be read.
    3. Explain historical context, dynasty, ruler, era and purpose
       only when supported by evidence.
    4. Translate the readable text into modern Telugu.
    5. Translate the readable text into modern English.
    6. Identify damaged, uncertain or illegible passages.
    7. Never invent missing text or unsupported historical facts.
       Separate confirmed details from tentative interpretations.

    Use this Markdown format:

    ### 📜 Historical Context
    Describe the likely period and historical setting.

    ### 🔤 Script Identification and Transcription
    Identify the script and transcribe readable text.

    ### 🇮🇳 Modern Telugu Translation (ఆధునిక తెలుగు భావం)
    Provide the Telugu meaning and mark uncertain passages.

    ### 🇬🇧 Modern English Translation
    Provide the English meaning.

    ### 📝 Notes and Uncertainties
    Explain damaged text, ambiguity and limitations.
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

    errors = []

    for model_name in models:
        status_box.info(
            f"🔎 Analyzing inscription with {model_name}..."
        )

        endpoint = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model_name}:generateContent"
        )

        try:
            response = requests.post(
                endpoint,
                params={"key": key},
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120
            )

            try:
                data = response.json()
            except ValueError:
                errors.append(
                    f"{model_name}: Invalid response from Google."
                )
                continue

            if response.status_code == 200:
                candidates = data.get("candidates", [])

                if candidates:
                    parts = candidates[0].get(
                        "content", {}
                    ).get("parts", [])

                    answer = "\n\n".join(
                        part["text"]
                        for part in parts
                        if "text" in part
                    )

                    if answer.strip():
                        status_box.success(
                            f"✅ Analysis completed using {model_name}."
                        )
                        return answer

                feedback = data.get("promptFeedback", {})
                reason = feedback.get(
                    "blockReason", "No text returned"
                )

                errors.append(f"{model_name}: {reason}")
                continue

            error_info = data.get("error", {})
            error_message = error_info.get(
                "message", "Unknown API error"
            )
            error_code = error_info.get(
                "code", response.status_code
            )
            error_status = error_info.get("status", "")

            errors.append(
                f"{model_name}: HTTP {error_code}: {error_message}"
            )

            lower_message = error_message.lower()

            # Try the next model for unavailable model IDs.
            model_issue = any(
                phrase in lower_message
                for phrase in [
                    "not found",
                    "not supported",
                    "unsupported",
                    "no longer available",
                    "no longer supported",
                    "update your code",
                ]
            )

            if model_issue:
                continue

            # A 429 can be model-specific. Try another eligible
            # model, but report quota failure if all attempts fail.
            if (
                error_code == 429
                or error_status == "RESOURCE_EXHAUSTED"
            ):
                continue

            # Invalid requests and authentication/permission errors
            # are unlikely to be fixed by switching models.
            if error_code in (400, 401, 403):
                return (
                    "❌ **Gemini rejected the request.**\n\n"
                    f"**Details:** {error_message}\n\n"
                    "Check the API key, permissions and request."
                )

        except requests.Timeout:
            errors.append(f"{model_name}: Request timed out.")

        except requests.RequestException as e:
            errors.append(f"{model_name}: Network error: {e}")

        except Exception as e:
            errors.append(f"{model_name}: {e}")

    combined_errors = "\n\n".join(
        f"- {error}" for error in errors[-8:]
    )

    # Make quota failures easier to recognize.
    if any(
        "429" in error
        or "quota" in error.lower()
        or "resource_exhausted" in error.lower()
        for error in errors
    ):
        return (
            "⚠️ **Gemini API quota or rate limit reached.**\n\n"
            "The app tried other eligible models, but the requests "
            "did not succeed. Check the quota and billing for your "
            "Google AI Studio project.\n\n"
            f"**Attempt details:**\n{combined_errors}"
        )

    return (
        "❌ **Translation failed.**\n\n"
        "No available model completed the request.\n\n"
        f"**Attempt details:**\n{combined_errors}"
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
                    Upload an inscription to explore its historical
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

    elif st.button(
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
