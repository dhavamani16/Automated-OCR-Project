# --- Project Component III: Back-End API Development (Flask Server) ---
# This file integrates the OCR logic (placeholder), Translation, and TTS.

import os
from flask import Flask, request, jsonify, send_file
# FIX: Changed import to use the 'translate' package, which is installed and stable.
from translate import Translator 
from gtts import gTTS

app = Flask(__name__)

# Define constants
TARGET_LANGUAGE = 'en'
OUTPUT_AUDIO_FILE = 'translation_output.mp3'
TEMP_UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(TEMP_UPLOAD_FOLDER, exist_ok=True)

# --- Core Logic from Component II (Translation & TTS) ---
def translate_and_speak(ocr_text: str, target_lang: str) -> dict:
    """
    Translates text and generates a local MP3 file.
    """
    if not ocr_text.strip():
        return {
            "success": False,
            "translated_text": "",
            "message": "OCR text is empty for translation.",
        }

    try:
        # Initializing translator using the 'translate' library.
        translator = Translator(to_lang=target_lang)
        translated_text = translator.translate(ocr_text)

        source_lang = "auto" 

        # Generate and save TTS audio
        tts = gTTS(text=translated_text, lang=target_lang)
        audio_path = os.path.join(TEMP_UPLOAD_FOLDER, OUTPUT_AUDIO_FILE)
        tts.save(audio_path)

        return {
            "success": True,
            "translated_text": translated_text,
            "source_language": source_lang,
            "audio_file_path": audio_path
        }
    except Exception as e:
        # Catch translation/TTS errors
        return {
            "success": False,
            "translated_text": "",
            "message": f"Translation/TTS failed: {e}",
        }

# --- Placeholder for OCR Logic (Component I) ---
def perform_ocr(image_file_path: str) -> str:
    """
    Placeholder function for Tesseract/OpenCV integration.
    In the final app, this would use a library like 'pytesseract'.
    """
    print(f"--- Simulating OCR on image: {image_file_path} ---")
    # Return a sample text to be translated, simulating a successful OCR scan
    return "Das ist ein Beispieltext, der von einer deutschen Seite gescannt wurde, und er wird jetzt übersetzt."


# --- API Routes ---

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    """
    Endpoint for the Flutter app to send an image and get translation/audio back.
    """
    # 1. Handle File Upload
    if 'image' not in request.files:
        return jsonify({"message": "No image file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "No selected image file"}), 400

    # Save the file temporarily
    image_path = os.path.join(TEMP_UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    # 2. Perform OCR (Component I)
    try:
        extracted_text = perform_ocr(image_path)
    except Exception as e:
        return jsonify({"message": f"OCR processing failed: {e}"}), 500
    
    # 3. Translate and Speak (Component II)
    results = translate_and_speak(extracted_text, target_lang=TARGET_LANGUAGE)

    if results["success"]:
        return jsonify({
            "original_text": extracted_text,
            "translated_text": results["translated_text"],
            "audio_url": request.url_root + 'get_audio'
        })
    else:
        # We need to clean up the temporary image if translation/TTS fails
        os.remove(image_path)
        return jsonify({"message": results["message"]}), 500

@app.route('/get_audio', methods=['GET'])
def get_audio():
    """
    Endpoint for the Flutter app to download the generated MP3 file.
    """
    audio_path = os.path.join(TEMP_UPLOAD_FOLDER, OUTPUT_AUDIO_FILE)
    if not os.path.exists(audio_path):
        return jsonify({"message": "Audio file not found"}), 404
        
    return send_file(
        audio_path,
        mimetype='audio/mp3',
        as_attachment=True,
        download_name=OUTPUT_AUDIO_FILE
    )

# --- Server Startup ---
if __name__ == '__main__':
    print("-----------------------------------------------------------------------")
    print("FLASK SERVER READY: The server will run the translation/TTS logic.")
    print("-----------------------------------------------------------------------")
    app.run(host='0.0.0.0', port=5000, debug=True)
