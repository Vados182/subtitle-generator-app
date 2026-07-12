# 🎬 AI Video Subtitle Generator

> Aplikacja webowa do automatycznego generowania, edycji, tłumaczenia i wtapiania napisów do filmów, oparta o modele OpenAI (Whisper & GPT-4).

## 🚀 O Projekcie

Aplikacja została stworzona, aby drastycznie skrócić czas potrzebny na tworzenie profesjonalnych napisów do materiałów wideo. Pozwala użytkownikom wgrać film, automatycznie wygenerować transkrypcję audio, przetłumaczyć ją na jeden z wielu obsługiwanych języków, ręcznie edytować tekst w interaktywnym edytorze i ostatecznie pobrać sam plik `.srt` lub gotowy film z wtopionymi ("hardcoded") napisami.

**💡 Zobacz działającą aplikację: [[LINK DO DZIAŁAJĄCEJ APLIKACJI - np. na Streamlit Cloud]]**

---

## 🛠️ Użyte Technologie & Architektura

Projekt został zaprojektowany z dbałością o separację logiki od interfejsu (Modular Architecture), co ułatwia testowanie i rozwój.

-   **Python (3.11)** - Główne środowisko programistyczne.
-   **Streamlit** - Framework do szybkiego tworzenia interfejsów webowych.
-   **OpenAI API** - Integracja z modelami Whisper (v3) i GPT-4.
-   **Pydub** - Biblioteka do manipulacji plikami audio.
-   **FFmpeg** - Zewnętrzne narzędzie systemowe do zaawansowanej konwersji i wtapiania napisów.
-   **Git** - System kontroli wersji.

### Struktura Projektu (Separation of Concerns):

W VS Code:
```text
├── .streamlit/config.toml  # Konfiguracja limitu 1GB w interfejsie Streamlit.
├── app.py                  # Główny plik, widoki i kontroler stanu aplikacji (Streamlit).
├── audio_processor.py      # Logika obróbki audio, walidacji i operacji systemowych (FFmpeg).
├── openai_service.py       # Klasa obsługująca komunikację z API OpenAI (Whisper & GPT).
├── requirements.txt        # Lista zależności Pythona.
├── .gitignore              # Lista plików ignorowanych przez Git (np. śmieci timery, __pycache__).
├── movie.jpg               # Obraz tła interfejsu.
└── translate.png           # Obraz paska bocznego.