import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io
import base64
import urllib.parse

# 1. Page Configuration
st.set_page_config(page_title="SARAL - AI Assistant", page_icon="📝", layout="centered")
st.title("📝 Project SARAL")
st.subheader("Bhaiya will help you fill the form!")

# 2. Secure AI Configuration (Pulled from Streamlit Cloud Secrets)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
    MODEL_ID = "gemini-3-flash" # The stable 2026 workhorse
except Exception as e:
    st.error("Secrets not configured! Please add GEMINI_API_KEY to your Streamlit Advanced Settings.")
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

# 3. Sidebar
with st.sidebar:
    st.header("Help & Settings")
    st.info("Scan any form to get step-by-step Hinglish instructions.")
    if st.button("🔄 Clear App"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# 4. Input Section
source = st.radio("Choose Input:", ["📷 Camera", "📁 Upload Image"], horizontal=True)
img_file = st.camera_input("Scan") if source == "📷 Camera" else st.file_uploader("Upload", type=["jpg", "png", "jpeg"])

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Document Captured", use_container_width=True)
    
    if st.button("Simplify Now ✨", type="primary"):
        with st.spinner("Bhaiya is reading the form..."):
            try:
                # The Professional Assistant Prompt
                prompt = """
                You are a helpful elder brother. 
                1. Identify the document type.
                2. Summarize it in 3 bullet points using simple HINGLISH.
                3. PROVIDE A STEP-BY-STEP FILLING GUIDE: Tell the user exactly what to write in each box/section seen in the image.
                4. Give one clear 'Next Step' (e.g., go to Bank Window 4).
                """
                
                response = client.models.generate_content(model=MODEL_ID, contents=[prompt, img])
                
                if response.text:
                    st.session_state.summary = response.text
                else:
                    st.warning("Photo clear nahi hai. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# 5. Output Section
if 'summary' in st.session_state:
    st.success("Analysis Ready!")
    st.markdown("### 💡 Brother's Guide (Hinglish):")
    st.write(st.session_state.summary)
    
    # --- Action Buttons ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔊 Read Aloud"):
            speak_text(st.session_state.summary)
            
    with col2:
        st.download_button("💾 Download", st.session_state.summary, file_name="saral_guide.txt")
        
    with col3:
        # WhatsApp Share
        msg = urllib.parse.quote(f"SARAL Assistant Guide: {st.session_state.summary[:150]}...")
        st.markdown(f'[<button style="background-color:#25D366;color:white;border:none;padding:8px;border-radius:5px;">🟢 WhatsApp</button>](https://wa.me/?text={msg})', unsafe_allow_html=True)

# 6. Footer
st.divider()
st.caption("Project SARAL 2026 | Digital India Assistance")
