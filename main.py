import streamlit as st
from engine import process_mumz_request, MumzPulseEngine
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io

st.set_page_config(
    page_title="MumzPulse AI Assistant",
    page_icon="👶",
    layout="centered"
)

st.title("👶 MumzPulse AI Assistant")
st.header("Milestone-Driven Shopping Assistant for Mumzworld")
st.markdown("---")

st.markdown("Tell us about your baby's milestone or concern (English or Arabic).")

# Initialize session state
if 'last_response_text' not in st.session_state:
    st.session_state.last_response_text = None
if 'last_response_audio' not in st.session_state:
    st.session_state.last_response_audio = None
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = ""
if 'last_audio_len' not in st.session_state:
    st.session_state.last_audio_len = 0
if 'recorder_key' not in st.session_state:
    st.session_state.recorder_key = 0

# ── Input Section ──
user_input = st.text_area(
    "Describe your situation",
    value=st.session_state.transcribed_text,
    placeholder="e.g., My 8-month-old started crawling / ابني بدأ يزحف",
    height=100,
    label_visibility="collapsed"
)

st.markdown("**Or record a voice memo:**")
audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹️ Stop",
    key=f'recorder_{st.session_state.recorder_key}'
)

if audio is not None:
    current_len = len(audio['bytes'])
    last_len = st.session_state.get('last_audio_len', 0)
    if current_len != last_len:
        st.session_state.last_audio_len = current_len
        with st.spinner("Transcribing..."):
            engine = MumzPulseEngine()
            transcribed = engine.transcribe_audio(audio['bytes'])
            st.session_state.transcribed_text = transcribed
            st.rerun()
    else:
        st.info("Voice memo recorded.")

col1, col2 = st.columns([1, 4])
with col1:
    analyze_button = st.button("Analyze", type="primary")
with col2:
    clear_button = st.button("Clear")

if clear_button:
    st.session_state.recorder_key += 1
    st.session_state.transcribed_text = ""
    st.session_state.last_audio_len = 0
    st.session_state.last_response_audio = None
    st.session_state.last_response_text = None
    st.rerun()

# ── Response Section ──
if analyze_button and user_input:
    with st.spinner("Analyzing..."):
        try:
            result = process_mumz_request(user_input)
        except Exception as e:
            st.error(f"Error: {str(e)}")
            result = None

    if result:
        response_text = None

        if result.get("medical_red_flag"):
            st.error("🚨 **Medical Emergency Detected**\n\nThis situation requires immediate medical attention. Please consult a healthcare professional or visit the nearest emergency room.")
            response_text = "Medical emergency detected. Seek immediate medical attention."
            if any('\u0600' <= c <= '\u06FF' for c in user_input):
                response_text = "تم اكتشاف حالة طبية طارئة. تتطلب هذه الحالة عناية طبية فورية."

        elif result.get("out_of_scope"):
            st.warning("⚠️ **Out of Scope**\n\nMumzPulse is designed for baby and maternity-related needs only.")
            response_text = "Out of scope. This tool is for baby and maternity needs only."
            if any('\u0600' <= c <= '\u06FF' for c in user_input):
                response_text = "خارج نطاق التطبيق. هذا الأداة مخصصة للرضع والأمهات فقط."

        else:
            milestone = result.get("detected_milestone")
            if milestone:
                st.success(f"🎯 **Detected Milestone:** {milestone.title()}")
            else:
                st.info("💡 **Recommendations**")

            recommendations = result.get("recommendations", [])
            if recommendations:
                st.markdown("### Recommended Products")
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}. {rec['name']}**")
                    st.markdown(f"   *{rec['reason']}*")
            else:
                st.info("No specific products found for this milestone.")

            expert_tip = result.get("expert_tip")
            if expert_tip:
                st.markdown("---")
                st.markdown(f"**💬 Expert Advice:**")
                st.write(expert_tip)
                response_text = expert_tip

        # Generate TTS audio for normal responses
        if response_text and not result.get("medical_red_flag") and not result.get("out_of_scope"):
            is_arabic = any('\u0600' <= c <= '\u06FF' for c in response_text)
            lang = 'ar' if is_arabic else 'en'
            try:
                with st.spinner("🎵 Generating audio briefing..."):
                    tts = gTTS(text=response_text, lang=lang, slow=False)
                    audio_buffer = io.BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    st.session_state.last_response_audio = audio_buffer
                    st.session_state.last_response_text = response_text
            except Exception as e:
                st.error(f"TTS generation failed: {e}")

elif analyze_button and not user_input:
    st.warning("Please share your baby's status update above.")

# ── Audio Playback ──
if st.session_state.last_response_audio:
    st.markdown("---")
    st.markdown("### 🔊 Listen to Advice")
    st.audio(st.session_state.last_response_audio, format='audio/mp3')
    st.caption("Play this while you tend to your baby.")

st.markdown("---")
st.caption("MumzPulse v2.0 | Powered by Mumzworld & Groq AI")
