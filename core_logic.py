from gtts import gTTS
from translate import Translator
import os
import io
import base64

def translate_and_encode(text_to_translate, source_lang='en', target_lang='es'):
    """
    Translates text, generates audio, and encodes the audio to Base64.
    """
    try:
        # 1. Translation using the 'translate' library
        translator = Translator(from_lang=source_lang, to_lang=target_lang)
        translated_text = translator.translate(text_to_translate)
        
        # 2. Voice Generation (gTTS) and Base64 Encoding
        tts = gTTS(text=translated_text, lang=target_lang)
        
        # Use an in-memory file (BytesIO)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        # Encode audio bytes to Base64 string
        encoded_audio = base64.b64encode(mp3_fp.read()).decode('utf-8')
        
        return translated_text, encoded_audio
        
    except Exception as e:
        print(f"Error in core_logic: {e}") 
        return "Error: Could not complete translation or audio generation.", None