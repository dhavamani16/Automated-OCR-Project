# This script demonstrates the translation and Text-to-Speech (TTS) components
# (Components I & II in your plan) and sets up the core logic for the back-end API.

# 1. Translation: Uses Google Translate (requires a key/service account)
#    NOTE: For simplicity and to run locally without cloud setup, we will use
#    the 'googletrans' library for the demonstration. If you must use
#    Google Cloud Translation API, the setup is different.

# 2. Text-to-Speech (TTS): Uses gTTS to convert text to an MP3 audio file.

import os
from googletrans import Translator
from gtts import gTTS

# --- Configuration ---
# Define the target language for translation
TARGET_LANGUAGE = 'en'
# Output file name for the speech audio
OUTPUT_AUDIO_FILE = 'translation_output.mp3'

def translate_and_speak(ocr_text: str, target_lang: str = TARGET_LANGUAGE) -> dict:
    """
    Takes OCR text, translates it, generates speech audio, and returns the results.

    Args:
        ocr_text (str): The text extracted by Tesseract/OpenCV.
        target_lang (str): The language code to translate the text into (e.g., 'en', 'fr').

    Returns:
        dict: A dictionary containing the original, translated text, and audio file path.
    """
    if not ocr_text.strip():
        return {
            "success": False,
            "message": "OCR text is empty.",
        }

    print(f"1. Original Text Received: \"{ocr_text[:50]}...\"")

    # --- Translation (Component II) ---
    try:
        translator = Translator()
        # Detect source language and translate
        translation = translator.translate(ocr_text, dest=target_lang)
        translated_text = translation.text
        source_lang = translation.src
        print(f"2. Translated Text ({source_lang} -> {target_lang}): \"{translated_text[:50]}...\"")

    except Exception as e:
        return {
            "success": False,
            "message": f"Translation failed: {e}",
        }

    # --- Text-to-Speech (TTS) (Component II) ---
    try:
        # Generate TTS audio for the translated text
        tts = gTTS(text=translated_text, lang=target_lang)
        tts.save(OUTPUT_AUDIO_FILE)
        print(f"3. Audio file saved to: {OUTPUT_AUDIO_FILE}")

    except Exception as e:
        return {
            "success": False,
            "message": f"TTS generation failed: {e}",
        }

    return {
        "success": True,
        "original_text": ocr_text,
        "translated_text": translated_text,
        "source_language": source_lang,
        "target_language": target_lang,
        "audio_file_path": os.path.abspath(OUTPUT_AUDIO_FILE)
    }

# --- Example Usage ---
if __name__ == "__main__":
    # Simulate text received from Component I (OCR process)
    sample_ocr_output = "Das ist ein Beispieltext, der von einer deutschen Seite gescannt wurde."

    results = translate_and_speak(sample_ocr_output)

    if results.get("success"):
        print("\n--- Process Complete ---")
        print(f"Original: {results['original_text']}")
        print(f"Translated: {results['translated_text']}")
        print(f"Audio Path: {results['audio_file_path']}")
        print("\nTo hear the audio, locate and play the translation_output.mp3 file in your ocr_test folder.")
    else:
        print(f"\n--- Error --- \n{results['message']}")
