import os
import base64
import streamlit as st
from audio_processor import AudioProcessor
from openai_service import OpenAIService

def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

current_dir = os.path.dirname(os.path.abspath(__file__))
main_bg = get_base64_of_bin_file(os.path.join(current_dir, "movie.jpg"))
sidebar_bg = get_base64_of_bin_file(os.path.join(current_dir, "translate.png"))

if main_bg and sidebar_bg:
    st.markdown(f"""
        <style>
        .stApp {{ background-image: url("data:image/jpg;base64,{main_bg}"); background-size: cover; background-attachment: fixed; }}
        [data-testid="stSidebar"] {{ background-image: url("data:image/jpg;base64,{sidebar_bg}"); background-size: contain; background-repeat: no-repeat; background-position: center; }}
        </style>
    """, unsafe_allow_html=True)

st.title("Generator Napisów")

# 1. Autoryzacja OpenAI
openai_key = st.text_input("Klucz API:", type="password")
if not openai_key:
    st.warning("Wprowadź klucz API, aby uruchomić aplikację.")
    st.stop()

openai_service = OpenAIService(openai_key)
if not openai_service.verify_key():
    st.error("Podany klucz API jest nieprawidłowy lub wygasł.")
    st.stop()

# 2. Słownik języków
languages_dict = {
    "Polski": "pl",
    "English": "en",
    "Deutsch": "de",
    "Français": "fr",
    "Español": "es",
    "Italiano": "it",
    "日本語": "ja",
    "中文": "zh"
}

if 'selected_lang' not in st.session_state:
    st.session_state['selected_lang'] = 'Polski'

with st.sidebar:
    st.header("Ustawienia Językowe")
    selected_lang = st.selectbox("Język napisów:", list(languages_dict.keys()))
    st.session_state['selected_lang'] = selected_lang

lang_code = languages_dict[st.session_state['selected_lang']]

# 3. Przesyłanie pliku 
supported_formats = ["mp4", "mp3", "mov", "avi", "mkv"]
uploaded_file = st.file_uploader("Wybierz plik wideo lub audio:", type=supported_formats)

if uploaded_file:
    file_ext = uploaded_file.name.lower().split('.')[-1]
    is_video = file_ext in ["mp4", "mov", "avi", "mkv"]

    # Podgląd (Streamlit natywnie odtwarza głównie MP4/MOV, dla innych formatów wyświetli odtwarzacz jeśli przeglądarka pozwala)
    if is_video:
        st.video(uploaded_file)
    else:
        st.audio(uploaded_file)

    # Walidacja rozmiaru dla Whisper API (25MB)
    if not AudioProcessor.validate_file_size(uploaded_file, max_mb=25):
        st.error("⚠️ Rozmiar pliku przekracza 25 MB.")
        st.info("💡 **Notatka architektoniczna:** Wideo o rozmiarze do 1 GB jest akceptowane przez aplikację, ale Whisper API przyjmuje porcje do 25 MB. Aby przetwarzać pliki 1 GB, należy zaimplementować chunking audio.")
        st.stop()

    base_name = uploaded_file.name.rsplit('.', 1)[0]
    output_audio_path = os.path.join(current_dir, f"temp_{base_name}.mp3")
    output_srt_path = os.path.join(current_dir, f"temp_{base_name}.srt")
    output_video_path = os.path.join(current_dir, f"burned_{base_name}.mp4")

    # Wyodrębnianie audio
    if st.session_state.get('last_file') != uploaded_file.name:
        with st.spinner("Wyodrębnianie i konwersja ścieżki dźwiękowej..."):
            AudioProcessor.extract_audio_to_mp3(uploaded_file, output_audio_path)
            st.session_state.last_file = uploaded_file.name
            if "original_srt_text" in st.session_state:
                del st.session_state.original_srt_text

    # Generowanie napisów bazowych
    if "original_srt_text" not in st.session_state:
        with st.spinner("Generowanie transkrypcji (OpenAI Whisper)..."):
            st.session_state.original_srt_text = openai_service.generate_srt(output_audio_path, lang_code)
            st.session_state.srt_text = st.session_state.original_srt_text
            st.session_state.lang_code_prev = lang_code

    # Logika tłumaczenia
    if lang_code != st.session_state.get('lang_code_prev'):
        with st.spinner(f"Tłumaczenie napisów na język: {st.session_state['selected_lang']}..."):
            translated = openai_service.translate_srt(st.session_state.original_srt_text, lang_code)
            st.session_state.srt_text = translated
            st.session_state.lang_code_prev = lang_code

    # Edycja tekstu SRT
    srt_text_edited = st.text_area("Edytor napisów SRT:", st.session_state.srt_text, height=200)
    st.session_state.srt_text = srt_text_edited

    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Pobierz sam plik .srt",
            data=st.session_state.srt_text,
            file_name=f"{base_name}.srt",
            mime="text/plain",
            use_container_width=True
        )

    # Wtapianie napisów w wideo (działa tylko jeśli wgrano wideo)
    with col2:
        if is_video:
            if st.button("🎬 Wtop napisy w wideo", use_container_width=True, type="primary"):
                with st.spinner("Trwa wtapianie napisów do pliku wideo (to może zająć dłuższą chwilę)..."):
                    success = AudioProcessor.burn_subtitles_to_video(uploaded_file, st.session_state.srt_text, output_srt_path, output_video_path)
                    if success and os.path.exists(output_video_path):
                        st.session_state.video_ready = True
                        st.session_state.ready_video_path = output_video_path
                    else:
                        st.error("Nie udało się wygenerować wideo z napisami. Upewnij się, że masz poprawnie zainstalowany FFmpeg.")

            # Przycisk pobierania gotowego filmu
            if st.session_state.get('video_ready') and os.path.exists(st.session_state.get('ready_video_path', '')):
                with open(st.session_state.ready_video_path, "rb") as video_file:
                    st.download_button(
                        label="🚀 Pobierz wideo z napisami (.mp4)",
                        data=video_file.read(),
                        file_name=f"subtitled_{base_name}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
        else:
            st.info("Wtapianie napisów jest niedostępne dla plików czysto dźwiękowych (MP3).")

    # Sprzątanie plików tymczasowych
    AudioProcessor.cleanup_file(output_audio_path)
    AudioProcessor.cleanup_file(output_srt_path)
else:
    st.info("Wgraj plik multimedialny, aby rozpocząć generowanie napisów.")
    if 'last_file' in st.session_state:
        del st.session_state.last_file
    st.session_state.video_ready = False