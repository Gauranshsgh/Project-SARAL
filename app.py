import streamlit as st
from google import genai
from PIL import Image
from gtts import gTTS
import io
import base64

# 1. Setup the Page
st.set_page_config(page_title="SARAL - AI Assistant", page_icon="📝")
st.title("📝 Project SARAL")
st.subheader("Bhaiya will help you fill the form!")

# 2. Configure the AI (2026 SDK)
API_KEY = "AIzaSyABM0po7Cv4ZWxrNpD8_Lpc-QfXNgcOevQ" 
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash" 

# --- Helper Function for Read Aloud ---
def speak_text(text):
    tts = gTTS(text=text, lang='hi') # Using 'hi' for Hinglish/Hindi natural sound
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    # Convert to base64 to autoplay in Streamlit
    audio_b64 = base64.b64encode(fp.read()).decode()
    audio_tag = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_b64}">'
    st.markdown(audio_tag, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.info("Step 1: Photo khinche.\nStep 2: 'Simplify' click karein.\nStep 3: Instructions suniye!")
    if st.button("🔄 Clear All"):
        st.rerun()

# 4. Input Method
source = st.radio("Input Type:", ["📷 Camera", "📁 Upload"], horizontal=True)
img_file = st.camera_input("Scan Form") if source == "📷 Camera" else st.file_uploader("Upload", type=["jpg", "png", "jpeg"])

if img_file:
    img = Image.open(img_file)
    st.image(img, caption="Form Loaded", use_container_width=True)
    
    if st.button("Simplify Now ✨", type="primary"):
        with st.spinner("Bhaiya form padh rahe hain..."):
            try:
                # NEW IMPROVED PROMPT
                prompt = """
                You are a helpful elder brother. Look at this form and:
                1. Identify exactly what this form is.
                2. Give a 3-step 'Form Filling Guide' in simple HINGLISH.
                3. For EACH major box/section in the image, tell the user exactly what to write there.
                4. End with a friendly 'All the best!'.
                """
                
                response = client.models.generate_content(model=MODEL_ID, contents=[prompt, img])
                
                if response.text:
                    st.session_state.summary = response.text
                    st.success("Analysis Complete!")
                else:
                    st.error("Photo clear nahi hai.")

            except Exception as e:
                st.error(f"Error: {e}")

    # Display Results and Audio Button
    if 'summary' in st.session_state:
        st.markdown("### 💡 Step-by-Step Guide:")
        st.write(st.session_state.summary)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔊 Read Aloud (Suniyé)"):
                speak_text(st.session_state.summary)
        with col2:
            st.download_button("💾 Download Text", st.session_state.summary, file_name="guide.txt")

# 5. Footer
st.divider()
st.caption("Project SARAL | Empowering Indians through AI.")