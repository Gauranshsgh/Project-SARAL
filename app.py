import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io
import base64
import urllib.parse

# 1. Page Configuration
st.set_page_config(page_title="SARAL - AI Assistant", page_icon="📝")
st.title("📝 Project SARAL")

# 2. Secure AI Configuration (Stable 2026 Model)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    # CHANGED: Swapped to 2.5-flash to fix the 404 NOT_FOUND error
    MODEL_ID = "gemini-2.5-flash" 
except Exception as e:
    st.error("Secrets missing! Check Streamlit Dashboard > Settings > Secrets.")
    st.stop()

# --- Helper Function for Read Aloud ---
def speak_text(text):
    tts = gTTS(text=text, lang='hi')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    audio_b64 = base64.b64encode(fp.read()).decode()
    audio_tag = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_b64}">'
    st.markdown(audio_tag, unsafe_allow_html=True)

# 3. Input Section
source = st.radio("Input:", ["📷 Camera", "📁 Upload"], horizontal=True)
img_file = st.camera_input("Scan") if source == "📷 Camera" else st.file_uploader("Upload", type=["jpg", "png", "jpeg"])

if img_file:
    img = Image.open(img_file)
    st.image(img, use_container_width=True)
    
    if st.button("Simplify Now ✨", type="primary"):
        with st.spinner("Bhaiya form padh rahe hain..."):
            try:
                prompt = """
                Explain this document as a helpful elder brother. 
                1. Identify the document. 
                2. 3-step guide in HINGLISH. 
                3. Exact instructions for filling the boxes.
                """
                # This call now uses the stable 2.5 model
                response = client.models.generate_content(model=MODEL_ID, contents=[prompt, img])
                
                if response.text:
                    st.session_state.summary = response.text
                else:
                    st.warning("Could not read text.")
            except Exception as e:
                st.error(f"Error: {e}")

# 4. Output Section
if 'summary' in st.session_state:
    st.markdown("### 💡 Brother's Guide:")
    st.write(st.session_state.summary)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔊 Suniye (Read Aloud)"):
            speak_text(st.session_state.summary)
    with col2:
        st.download_button("💾 Download", st.session_state.summary, file_name="guide.txt")

st.divider()
st.caption("Project SARAL 2026")
