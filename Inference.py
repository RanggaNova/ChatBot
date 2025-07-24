import os
from dotenv import load_dotenv
import google.generativeai as genai

def get_gemini_model():
    """
    Menginisialisasi dan mengembalikan model Generative AI dari Google.
    API key dibaca dari environment variables.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash-lite")
            return model
        except Exception as e:
            print(f"Error saat konfigurasi Gemini: {e}")
            return None
    
    print("GEMINI_API_KEY tidak ditemukan di environment variables.")
    return None

def transcribe_audio(model, audio_file_path):
    """
    Mengirim file audio ke model Gemini untuk transkripsi.

    Args:
        model: Instance dari GenerativeModel.
        audio_file_path (str): Path ke file audio.

    Returns:
        str: Teks hasil transkripsi atau None jika gagal.
    """
    if not model:
        return "Model Gemini tidak terinisialisasi."

    try:
        audio_file = genai.upload_file(
            path=audio_file_path,
            display_name="recorded_audio"
        )

        prompt = "Transcribe this audio. Return only the transcribed text, without any introductory phrases or explanations."
        
        response = model.generate_content([prompt, audio_file])
        
        genai.delete_file(name=audio_file.name)

        return response.text.strip()
        
    except Exception as e:
        print(f"Error saat transkripsi audio: {e}")
        try:
            if 'audio_file' in locals() and audio_file:
                genai.delete_file(name=audio_file.name)
        except Exception as delete_error:
            print(f"Gagal menghapus file saat error handling: {delete_error}")
            
        return f"Terjadi kesalahan saat transkripsi: {e}"


def chat_bot(model, history, persona=""):
    """
    Menghasilkan respons dari chatbot berdasarkan riwayat percakapan.

    Args:
        model: Instance dari GenerativeModel.
        history (list): Riwayat percakapan.
        persona (str): Persona atau instruksi sistem untuk model.

    Returns:
        str: Respons teks dari model.
    """
    if not model:
        return "Model Gemini tidak terinisialisasi. Periksa API key Anda."

    new_history = history.copy()
    if persona:
        new_history.insert(0, {"role": "user", "parts": [persona]})
    
    try:
        response = model.generate_content(new_history)
        return response.text
    except Exception as e:
        print(f"Error saat generate content: {e}")
        return f"Terjadi kesalahan saat menghubungi API Gemini: {e}"
