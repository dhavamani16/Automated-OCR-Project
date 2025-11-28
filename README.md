Signboard Translator

Signboard Translator is an AI-powered system that extracts text from signboard images and translates it into multiple languages, including Tamil. It also provides audio output, making signboards more accessible for everyone. The system uses Tesseract OCR for text extraction and Gemini Generative AI for translation.

Features

Text Extraction: Uses Tesseract OCR to read text from signboard images.

Multi-language Translation: Translate extracted text into multiple languages.

Audio Output: Text-to-Speech (TTS) functionality using gTTS for audio playback.

Real-time Processing: Integrated Flutter mobile app communicates with a Flask backend for seamless operation.

Technical Architecture

Stage 1: OCR and Text Extraction

Capture or upload a signboard image.

Extract text using Tesseract OCR.

Detect the language of the extracted text.

Stage 2: Translation and Audio Generation

Translate the extracted text using Gemini Generative AI.

Generate audio output using gTTS for the translated text.

Return translated text and audio to the Flutter mobile app for display/playback.

Setup Instructions

Clone the repository.

Install dependencies:

pip install -r requirements.txt


Obtain the Gemini API key and update .env:

GEMINI_API_KEY=your_api_key_here


Run the Flask backend:

python app.py


Open the Flutter mobile app and connect it to the backend.

Usage

Open the Flutter app on your mobile device.

Capture or upload a signboard image.

The app will display the extracted text and translated version.

Tap the audio button to listen to the translation.

License & Terms

Copyright (C) Codebasics Inc. All rights reserved.

Licensed under the MIT License.

Commercial use is prohibited without prior written permission.

Attribution must be given in all copies or substantial portions of the software.
