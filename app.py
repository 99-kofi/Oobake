# obala_ga_app.py
# Streamlit-based Oobakɛ GA chat with Gemini and Text-to-Speech output (Ga Error Messages)
# NOTE: This file contains a HARDCODED API KEY PLACEHOLDER for demo purposes.
# For production, store the key in an environment variable instead.

import streamlit as st
import requests
import json
from gradio_client import Client
import os
import logging
from PIL import Image

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyDpAmrLDJjDTKi7TD-IS3vqQlBAYVrUbv4" # <-- IMPORTANT: REPLACE THIS
MODEL_NAME = "gemini-2.0-flash"
TTS_MODEL = "Ghana-NLP/Southern-Ghana-TTS-Public"

# Configure logging to show technical errors in the console (for the developer)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Ga Error Messages for the User ---
GA_ERRORS = {
    "TTS_CONNECTION_FAILED": "Minaa, mibako jaje gbɛi gbáaŋ nɛɛ kɛkɔ nɔ. Boaŋ ni okɛŋa eko dã.",
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
        width: 100%; /* Make buttons fill the column */
    }
    /* Add some space below each starter group */
    .stButton {
        margin-bottom: 5px;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        margin-bottom: 15px;
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
st.info("You can type your prompts in either Ga or English.")

tts_client = init_tts_client()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Afii oŋŋ! Miŋa Oobakɛ. Te mi nyɛŋ miboa boŋ?"}
    ]

# --- Function to handle button clicks for conversation starters ---
def send_starter(starter_text):
    st.session_state.messages.append({"role": "user", "content": starter_text})
    st.rerun()

# --- Conversation Starters Section ---
st.markdown("---")
st.markdown("<h4 style='text-align: center; color: grey;'>Bɔi Sanegbaa</h4>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("Okɛɛ mi adesaahi"):
        send_starter("Okɛɛ mi adesaahi")
    st.caption("Tell me a story")

    if st.button("Te ŋwɛi yɔɔ tɛŋŋ ŋmɛnɛ?"):
        send_starter("Te ŋwɛi yɔɔ tɛŋŋ ŋmɛnɛ?")
    st.caption("What is the weather like today?")

with col2:
    if st.button("Ŋmaa wiemɔ yɛ Faa Tɛle he"):
        send_starter("Ŋmaa wiemɔ yɛ Faa Tɛle he")
    st.caption("Write a short poem about the Ocean")

    if st.button("Tsɔɔ 'Oobakɛ, te oyɔɔ tɛŋŋ?' shishi"):
        send_starter("Tsɔɔ 'Oobakɛ, te oyɔɔ tɛŋŋ?' shishi")
    st.caption("Translate 'Oobakɛ, te oyɔɔ tɛŋŋ?'")
st.markdown("---")


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


# --- Handle New User TEXT Input ---
if prompt := st.chat_input("Ŋma boŋ Ga kɛŋa..."):
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
                    "generationConfig": {"temperature": 0.2, "maxOutputTokens": 80}
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
        
