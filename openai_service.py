from openai import OpenAI

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def verify_key(self) -> bool:
        """Weryfikuje poprawność klucza API."""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False

    def generate_srt(self, audio_path: str, lang_code: str) -> str:
        """Generuje napisy SRT za pomocą modelu Whisper."""
        with open(audio_path, "rb") as f:
            transcript = self.client.audio.transcriptions.create(
                file=f,
                model="whisper-1",
                response_format="srt",
                language=lang_code
            )
        return transcript

    def translate_srt(self, srt_text: str, target_lang_code: str) -> str:
        """Tłumaczy strukturę SRT przy użyciu gpt-4o-mini."""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert subtitle translator. Translate the text but keep all SRT timecodes, line numbers, and formatting exactly intact."
                },
                {
                    "role": "user", 
                    "content": f"Translate this SRT content to {target_lang_code}:\n\n{srt_text}"
                },
            ],
            temperature=0,
        )
        return response.choices[0].message.content