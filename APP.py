import streamlit as st
from PIL import Image
from rembg import remove
import io
import os
from streamlit_mic_recorder import mic_recorder

# Import fungsi dari file Inference.py
from Inference import get_gemini_model, chat_bot, transcribe_audio

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Gemini Chat & Tools", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Inisialisasi Model Gemini ---
if 'gemini_model' not in st.session_state:
    try:
        os.environ['GEMINI_API_KEY'] = st.secrets['GEMINI_API_KEY']
    except (KeyError, FileNotFoundError):
        pass # Biarkan get_gemini_model menangani dari .env jika secrets tidak ada
    st.session_state.gemini_model = get_gemini_model()

if not st.session_state.gemini_model:
    st.error("⚠️ Kunci API Gemini tidak ditemukan. Mohon atur di file .env atau di Streamlit secrets.")
    st.stop()

# --- Judul Aplikasi dan Persona ---
st.title("🤖 Gemini Chat & Tools")
custom_persona = (
    "Kamu adalah Bot yang dibuat oleh Rangga Novalino Safitrah menggunakan Gemini API, "
    "seorang AI assistant yang ramah, pintar, dan suka membantu. Jawabanmu harus mudah dimengerti dan sopan."
)

# --- Inisialisasi Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_memory" not in st.session_state:
    st.session_state.chat_memory = []
if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

# --- Tampilkan Riwayat Chat ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "content" in message:
            st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"], caption=message.get("caption"), width=300)
        if "download_button" in message:
            btn_info = message["download_button"]
            st.download_button(**btn_info)

# ==========================================================
# --- AREA INPUT PENGGUNA ---
# ==========================================================
st.markdown("---")

# Kolom untuk tombol upload dan rekam
col1, col2 = st.columns([0.5, 0.5], gap="small")
with col1:
    uploaded_file = st.file_uploader(
        "🖼️ Hapus Background",
        type=["png", "jpg", "jpeg"],
        label_visibility="visible"
    )
with col2:
    st.write("🎙️ Kirim Pesan Suara")
    audio_info = mic_recorder(
        start_prompt="Rekam",
        stop_prompt="Stop",
        just_once=True,
        key='mic'
    )

# Input teks utama
text_prompt = st.chat_input("Ketik pesan, unggah gambar, atau rekam suara...")

# --- Logika Pemrosesan Input ---

final_prompt = text_prompt
transcribed_text = None

# 👉 1. Proses rekaman suara jika ada
if audio_info:
    audio_bytes = audio_info['bytes']
    audio_filename = "temp_audio.wav"
    
    with open(audio_filename, "wb") as f:
        f.write(audio_bytes)

    with st.spinner("Mentranskripsi suara... ✍️"):
        transcribed_text = transcribe_audio(st.session_state.gemini_model, audio_filename)
        os.remove(audio_filename)

    if transcribed_text and "Terjadi kesalahan" not in transcribed_text:
        final_prompt = transcribed_text
    else:
        st.error(f"Gagal mentranskripsi: {transcribed_text or 'Hasil kosong.'}")
        st.stop()

# 👉 2. Proses gambar yang diunggah jika ada
elif uploaded_file is not None:
    if st.session_state.last_uploaded != uploaded_file.name:
        st.session_state.last_uploaded = uploaded_file.name

        user_msg_content = f"Tolong hapus background dari gambar `{uploaded_file.name}`."
        st.session_state.messages.append({"role": "user", "content": user_msg_content})
        
        with st.chat_message("user"):
            st.markdown(user_msg_content)
            st.image(uploaded_file, width=300)

        with st.chat_message("assistant"):
            with st.spinner("Menghapus background... 🪄"):
                input_img = Image.open(uploaded_file)
                output_img = remove(input_img)
                buf = io.BytesIO()
                output_img.save(buf, format="PNG")
                byte_im = buf.getvalue()

                assistant_msg = {
                    "role": "assistant",
                    "content": "Berikut hasilnya:",
                    "image": output_img,
                    "caption": "Hasil Tanpa Background",
                    "download_button": {
                        "label": "💾 Download Hasil",
                        "data": byte_im,
                        "file_name": f"bg_removed_{uploaded_file.name}",
                        "mime": "image/png"
                    }
                }
                st.session_state.messages.append(assistant_msg)
        st.rerun()

# 👉 3. Proses prompt teks (dari chat input atau transkripsi)
if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    st.session_state.chat_memory.append({"role": "user", "parts": [final_prompt]})

    with st.chat_message("user"):
        st.markdown(final_prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("AI sedang berpikir... 🤔"):
            response_text = chat_bot(
                st.session_state.gemini_model,
                st.session_state.chat_memory,
                custom_persona
            )
            st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.session_state.chat_memory.append({"role": "model", "parts": [response_text]})
    st.rerun()
