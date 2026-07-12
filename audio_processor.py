import os
import subprocess
from pydub import AudioSegment

class AudioProcessor:
    @staticmethod
    def validate_file_size(uploaded_file, max_mb=25) -> bool:
        """
        Sprawdza, czy plik nie przekracza limitu wielkości dla OpenAI Whisper (25 MB).
        """
        max_bytes = max_mb * 1024 * 1024
        return uploaded_file.size <= max_bytes

    @staticmethod
    def extract_audio_to_mp3(uploaded_file, output_name="temp_audio.mp3") -> str:
        """
        Wyodrębnia ścieżkę dźwiękową i zapisuje ją jako zoptymalizowany plik MP3.
        Używa pydub, który wymaga FFmpeg w systemie.
        """
        try:
            audio = AudioSegment.from_file(uploaded_file)
            audio.export(output_name, format="mp3")
            return output_name
        except Exception as e:
            raise RuntimeError(f"Błąd podczas przetwarzania pliku audio/wideo przez Pydub: {str(e)}")

    @staticmethod
    def burn_subtitles_to_video(uploaded_video, srt_content, temp_srt_path, output_video_path) -> bool:
        """
        Wtapia napisy SRT bezpośrednio w plik wideo przy użyciu systemowego FFmpeg.
        Ta metoda wymaga zainstalowanego i dostępnego w PATH narzędzia FFmpeg.
        """
        temp_input_video = None
        try:
            # 1. Zapisujemy aktualną treść napisów z edytora do pliku tymczasowego .srt
            with open(temp_srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

            # 2. Zapisujemy przesłany przez użytkownika plik wideo tymczasowo na dysk
            # aby FFmpeg mógł go odczytać.
            file_ext = uploaded_video.name.split('.')[-1]
            temp_input_video = f"temp_input_video_{uploaded_video.file_id}.{file_ext}"
            with open(temp_input_video, "wb") as f:
                f.write(uploaded_video.getbuffer())

            # 3. Przygotowanie filtra FFmpeg. Ścieżka do SRT musi być specjalnie sformatowana,
            # szczególnie na Windowsie, aby FFmpeg ją przyjął.
            # Zamieniamy \ na / i uciekamy dwukropek (np. C\:).
            srt_filter_path = temp_srt_path.replace("\\", "/").replace(":", "\\:")
            
            # Komenda FFmpeg do wtapiania napisów (hardcoding subtitles)
            # -y: nadpisanie pliku wyjściowego
            # -i: plik wejściowy
            # -vf: filtr wideo (subtitles)
            # -c:a copy: kopiowanie ścieżki audio bez re-enkodowania (przyspiesza proces)
            cmd = [
                'ffmpeg', '-y', 
                '-i', temp_input_video, 
                '-vf', f"subtitles='{srt_filter_path}'", 
                '-c:a', 'copy', 
                output_video_path
            ]

            # Uruchomienie procesu w systemie (wymaga FFmpeg w PATH)
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
            
            # Sprawdzenie kodu powrotu (0 oznacza sukces)
            if process.returncode == 0:
                return True
            else:
                # Wypisujemy błąd FFmpeg do konsoli/loga, aby ułatwić debugowanie
                print(f"BŁĄD FFmpeg (burn_subtitles): {process.stderr}")
                return False
                
        except Exception as e:
            print(f"WYJĄTEK podczas wtapiania napisów: {str(e)}")
            return False
        finally:
            # Gwarantujemy posprzątanie tymczasowego pliku wideo wejściowego
            if temp_input_video:
                AudioProcessor.cleanup_file(temp_input_video)

    @staticmethod
    def cleanup_file(file_path: str):
        """
        Bezpiecznie usuwa plik tymczasowy z dysku.
        """
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Nie udało się usunąć pliku tymczasowego {file_path}: {str(e)}")