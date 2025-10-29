from flask import Flask, request, jsonify
from core_logic import translate_and_encode 

app = Flask(__name__)

@app.route('/translate_audio', methods=['POST'])
def translate_audio_endpoint():
    # 1. Get data from the mobile app
    data = request.get_json()
    
    text = data.get('text')
    source_lang = data.get('source_lang', 'en')
    target_lang = data.get('target_lang', 'es')
    
    if not text:
        return jsonify({"error": "Please provide text to translate."}), 400

    # 2. Call the core translation/voice logic
    translated_text, encoded_audio = translate_and_encode(text, source_lang, target_lang)

    # 3. Prepare the final JSON response
    if encoded_audio:
        response_data = {
            "translated_text": translated_text,
            "audio_base64": encoded_audio,
            "success": True
        }
        return jsonify(response_data), 200
    else:
        return jsonify({"error": translated_text, "success": False}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)