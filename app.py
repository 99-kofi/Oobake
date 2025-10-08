# obala_ga_app.py
# Streamlit-based Oobakɛ GA chat with Gemini and Text-to-Speech output (Ga Error Messages)
# NOTE: This file contains a HARDCODED API KEY PLACEHOLDER for demo purposes.
# For production, store the key in an environment variable instead.

import streamlit as st
import requests
import json
from gradio_client import Client, handle_file
import os
import logging
from PIL import Image
import tempfile
from streamlit_mic_recorder import mic_recorder

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyDpAmrLDJjDTKi7TD-IS3vqQlBAYVrUbv4" # <-- IMPORTANT: REPLACE THIS
MODEL_NAME = "gemini-2.0-flash"
TTS_MODEL = "Ghana-NLP/Southern-Ghana-TTS-Public"
STT_MODEL = "DarliAI/Evaluation" # Using the specialized DarliAI model for Ga

# Configure logging to show technical errors in the console (for the developer)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Ga Error Messages for the User ---
GA_ERRORS = {
    "TTS_CONNECTION_FAILED": "Minaa, mibako jaje gbɛi gbáaŋ nɛɛ kɛkɔ nɔ. Boaŋ ni okɛŋa eko dã.",
    "STT_CONNECTION_FAILED": "Minaa, wiemɔ nuɔŋmɔ nɛɛ he gbɛɛmɔ eyako. Boaŋ ni okɛŋa eko dã.",
    "TRANSCRIPTION_FAILED": "Minaa, minuɔ bo wiemɔ shɛɛɛ. Wie waa fio.",
    "GEMINI_API_FAILED": "Minaa, m'atsɛŋŋ gbáaŋ nɛɛ he nii yɛ gbɛ ni dɔŋŋ. Boaŋ ni okɛŋa eko dã.",
    "AUDIO_GENERATION_FAILED": "Minaa, sane ko bashɛ mi kɛjɛ gbɛi gbáaŋ he nɔ. Mi nyɛŋ mimá gbɛi nɛɛ.",
    "INVALID_AUDIO_PATH": "Gbɛi gbáaŋ nɛɛ kɛŋa mi gbɛ ni he ehiaŋ. Mi nyɛŋ mihe gbɛi nɛɛ.",
    "AUDIO_PATH_NOT_FOUND": "Miŋmɛ gbɛ nɛɛ deŋ, shi gbɛi gbáaŋ nɛɛ bɛ jɛi. Minaa.",
    "TRANSLATION_FAILED": "Minaa, mi nyɛŋ mikpala nɔ ni aŋma nɛɛ he."
}


# --- Main App ---
try:
    logo = Image.open("obpic.png")
    st.set_page_config(page_title="Oobakɛ GA", page_icon=logo, layout="centered")
except FileNotFoundError:
    st.set_page_config(page_title="Oobakɛ GA", page_icon="🇬🇭", layout="centered")


# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stButton>button {
        padding: 0.25rem 0.75rem;
        font-size: 0.85rem;
        line-height: 1.5;
        border-radius: 0.5rem;
        min-height: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Helper Functions ---
@st.cache_resource
def init_tts_client():
    try: return Client(TTS_MODEL)
    except Exception as e:
        logging.error(f"TTS client connection failed: {e}")
        st.error(GA_ERRORS["TTS_CONNECTION_FAILED"])
        return None

@st.cache_resource
def init_stt_client():
    try: return Client(STT_MODEL)
    except Exception as e:
        logging.error(f"STT client (DarliAI) connection failed: {e}")
        st.error(GA_ERRORS["STT_CONNECTION_FAILED"])
        return None

def translate_text(text_to_translate, target_language="English"):
    try:
        prompt = f"Translate the following Ga text to {target_language}. Do not add any preamble, just the translation: '{text_to_translate}'"
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2, "maxOutputTokens": 400}}
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
        res = requests.post(api_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
        res.raise_for_status()
        data = res.json()
        translated_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", GA_ERRORS["TRANSLATION_FAILED"])
        return translated_text.strip()
    except Exception as e:
        logging.error(f"Translation API call failed: {e}")
        return GA_ERRORS["TRANSLATION_FAILED"]

# --- Main Application Logic ---
st.title("🇬🇭 Oobakɛ — Ga AI Assistant")
st.caption("O- Omni-knowledgeable • O- Open-minded • B- Bilingual • A- African (Ga-focused) • K- Kind • Ɛ- Engaging")
st.caption("From WAIT ❤")
st.info("Okɛɛ wiemɔ loo oŋma yɛ Ga aloo Blofo mli.")

tts_client = init_tts_client()
stt_client = init_stt_client() # Initialize STT client

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Afii oŋŋ! Miŋa Oobakɛ. Te mi nyɛŋ miboa boŋ?"}
    ]

# --- Display Chat History ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "audio" in msg and msg["audio"]:
            if isinstance(msg["audio"], str) and os.path.isfile(msg["audio"]):
                st.audio(msg["audio"])

        if msg["role"] == "assistant" and msg["content"] not in GA_ERRORS.values():
            visibility_key = f"translation_visible_{i}"
            if visibility_key not in st.session_state:
                st.session_state[visibility_key] = False
            button_text = "Hide Translation" if st.session_state[visibility_key] else "See Translation"
            if st.button(button_text, key=f"translate_btn_{i}"):
                st.session_state[visibility_key] = not st.session_state[visibility_key]
                st.rerun()
            if st.session_state[visibility_key]:
                with st.spinner("Translating..."):
                    translation_cache_key = f"translation_text_{i}"
                    if translation_cache_key not in st.session_state:
                        st.session_state[translation_cache_key] = translate_text(msg["content"])
                    st.info(st.session_state[translation_cache_key])


# --- VOICE AND TEXT INPUT SECTION ---
audio_info = mic_recorder(start_prompt="🎤 Wie (Speak)", stop_prompt="⏹️ Mɔɔ shi (Stop)", just_once=True, key='recorder')
prompt = st.chat_input("Ŋma boŋ Ga kɛŋa...")

# Handle voice input
if audio_info and audio_info['bytes']:
    audio_bytes = audio_info['bytes']
    with st.spinner("Oobakɛ kɛ bo gbeɛ mli... (Transcribing...)"):
        transcribed_text = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_audio_file:
                tmp_audio_file.write(audio_bytes)
                tmp_audio_filepath = tmp_audio_file.name

            if stt_client:
                result = stt_client.predict(
                    audio_path=handle_file(tmp_audio_filepath),
                    language="Ga", # <-- Set language to Ga
                    api_name="/_transcribe_and_store"
                )
                transcribed_text = result if isinstance(result, str) else str(result)
            
            os.remove(tmp_audio_filepath)

        except Exception as e:
            logging.error(f"An unexpected transcription error occurred: {e}")
            st.error(GA_ERRORS["TRANSCRIPTION_FAILED"])

        if transcribed_text and transcribed_text.strip():
            st.session_state.messages.append({"role": "user", "content": transcribed_text})
            st.rerun()

# Handle text input
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()


# --- Generate and Display AI Response (if last message was from user) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner("Oobakɛ kɛjɛŋŋ kpeeŋ..."):
            text_reply = ""
            try:
                # Stricter prompt for short, factual answers
                system_prompt = "You are Oobakɛ, a friendly and knowledgeable AI assistant. Your primary language is Ga. You MUST ALWAYS reply in Ga. Understand the user's input (in English or Ga) and provide a helpful response. Crucial instruction: Your response must be extremely short and concise, ideally one sentence. Never write long paragraphs. If you do not know the answer, politely say 'Minaa'. Decline any requests that are harmful or unethical."
                
                gemini_messages = [{"role": ("model" if m["role"] == "assistant" else "user"), "parts": [{"text": m["content"]}]} for m in st.session_state.messages]
                
                payload = {
                    "contents": gemini_messages,
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 80} # Stricter controls
                }
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
                res = requests.post(api_url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
                res.raise_for_status()
                data = res.json()
                text_reply = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", GA_ERRORS["GEMINI_API_FAILED"])
            except Exception as e:
                logging.error(f"Gemini API call failed: {e}")
                text_reply = GA_ERRORS["GEMINI_API_FAILED"]
                st.error(text_reply)

        if text_reply and text_reply != GA_ERRORS["GEMINI_API_FAILED"]:
             st.markdown(text_reply)

        # Generate audio for the new response
        audio_path_to_store = None
        if text_reply and tts_client and text_reply != GA_ERRORS["GEMINI_API_FAILED"]:
            with st.spinner("Oobakɛ miwieŋ gbɛiŋ..."):
                audio_result = None
                try:
                    filepath_str = None
                    audio_result = tts_client.predict(text=text_reply, lang="Ga", speaker="Female", api_name="/predict")

                    if isinstance(audio_result, str):
                        filepath_str = audio_result
                    elif isinstance(audio_result, dict) and 'name' in audio_result and isinstance(audio_result['name'], str):
                        filepath_str = audio_result['name']

                    if filepath_str and os.path.isfile(filepath_str):
                        st.audio(filepath_str)
                        audio_path_to_store = filepath_str
                    else:
                        logging.warning(f"Audio generation failed: Path is not a valid file -> '{filepath_str}'")
                        st.warning(GA_ERRORS["AUDIO_PATH_NOT_FOUND"])

                except Exception as e:
                    logging.error(f"An error occurred during audio generation: {e}")
                    st.error(GA_ERRORS["AUDIO_GENERATION_FAILED"])

        # Add the complete AI response to history
        st.session_state.messages.append({"role": "assistant", "content": text_reply, "audio": audio_path_to_store})
        st.rerun()
