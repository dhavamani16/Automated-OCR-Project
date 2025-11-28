project-signboard-translator

This tool extracts text from signboard images and translates it into multiple languages including Tamil. It also provides audio output, making signboards more accessible for everyone.

<img width="1920" height="1008" alt="Screenshot 2025-11-17 210033" src="https://github.com/user-attachments/assets/b6114030-cfd0-4efc-8d7b-eb54381b02fa" />


Let's say a user is traveling and sees a signboard in an unfamiliar language. They can capture or upload an image of the signboard using this tool. The system extracts the text, translates it into the chosen language, and plays an audio version of the translation for easier understanding.

Technical Architecture
<img src="resources/architecture.jpg"/>

Stage 1: Capture or upload a signboard image. Extract text from it using Tesseract OCR and detect the source language.

Stage 2: Translate the extracted text using Gemini Generative AI. Generate audio output using gTTS. The Flutter app displays the translated text and plays the audio.

Set-up

First, get an API key from Gemini API
. Update .env with your key:

GEMINI_API_KEY=your_api_key_here


Install dependencies:

pip install -r requirements.txt


Run the Flask backend:

python app.py


Open the Flutter app and connect it to the backend.

Copyright (C) Codebasics Inc. All rights reserved.

Additional Terms:
This software is licensed under the MIT License. However, commercial use of this software is strictly prohibited without prior written permission from the author. Attribution must be given in all copies or substantial portions of the software.
