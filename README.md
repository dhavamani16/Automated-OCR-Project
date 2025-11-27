AI Signboard Translator

Flutter + Flask API + Tesseract OCR + Gemini AI + gTTS

An AI-powered mobile application that extracts text from signboard images and translates it into multiple languages (including Tamil). The system also provides audio output for accessibility.

🧠 Features

 Image Input – Capture using camera or select from gallery

 OCR Extraction – Uses Tesseract OCR to extract text from signboards

 AI Translation – Translates extracted text into any target language using Google Gemini API

 Text-to-Speech – Generates speech output via gTTS

 Flutter + Flask Integration – Real-time communication between app and backend

 Modern UI – Clean, simple and responsive Flutter interface

 Tech Stack
Frontend

Flutter

Dart

Material UI

Backend

Python

Flask

Tesseract OCR

Gemini Generative AI

gTTS (Google Text-to-Speech)

📸 Screenshot

Add your screenshot like this (replace URL with GitHub raw link):

![AI Translator Screenshot](https://github.com/yourusername/yourrepo/assets/screenshot.png)


Example (your attached screenshot):

![Screenshot](assets/translator_ui.png)

 How It Works
1. Upload or Capture Image

User selects a signboard image via camera or gallery.

2. OCR Processing

Backend uses:

pytesseract.image_to_string(image)


to extract text.

3. AI Translation

Extracted text is sent to Gemini API:

model.generate_content(f"Translate this to {target_lang}: {text}")

4. Audio Output

gTTS converts translation to speech:

gTTS(translated_text, lang=lang).save("output.mp3")

5. Response Returned to Flutter

Flutter displays extracted text + translated text + audio playback button.

📂 Project Structure
/flutter_app
    /lib
        main.dart
        screens/
        widgets/
    /assets

/flask_backend
    app.py
    ocr.py
    translator.py
    static/

🔧 Installation & Setup
Backend Setup
git clone <your-backend-repo>
cd flask_backend
pip install -r requirements.txt
python app.py

Frontend Setup
cd flutter_app
flutter pub get
flutter run

🛠 API Endpoints
Method	Endpoint	Description
POST	/extract	Extract text using OCR
POST	/translate	Translate text using AI
POST	/tts	Generate audio from text
📦 Requirements (Backend)

Python 3.9+

Flask

pytesseract

pillow

google-generativeai

gTTS

🙌 Contribution

Feel free to raise issues or submit pull requests.

📄 License

MIT License
