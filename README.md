<h1 style="font-family: 'Arial Black', sans-serif; color:#1F618D;"> Project: Signboard Translator</h1>

<p style="font-family: 'Verdana', sans-serif; font-size:16px;">
Signboard Translator is an AI-powered system that extracts text from signboard images and translates it into multiple languages, including Tamil. It also provides audio output, making signboards more accessible for everyone. The system uses Tesseract OCR for text extraction and Gemini Generative AI for translation.
</p>

<img width="9000" height="500" alt="Screenshot 2025-11-17 210033" src="https://github.com/user-attachments/assets/b6114030-cfd0-4efc-8d7b-eb54381b02fa" />

<p style="font-family: 'Verdana', sans-serif; font-size:16px;">
Imagine a user traveling in an unfamiliar area. They can capture or upload a <b>signboard image</b> using this tool. The system will:
</p>

<ul style="font-family: 'Verdana', sans-serif; font-size:16px;">
<li>Extract the text using <b>Tesseract OCR</b></li>
<li>Translate it using <b>Gemini Generative AI</b></li>
<li>Play an audio version using <b>gTTS</b></li>
</ul>

<h2 style="font-family: 'Arial Black', sans-serif; color:#1F618D;"> Technical Architecture</h2>

<ol style="font-family: 'Verdana', sans-serif; font-size:16px;">
<li><b>Stage 1: OCR & Text Extraction</b>
<ul>
<li>Capture or upload a signboard image.</li>
<li>Extract text using <b>Tesseract OCR</b>.</li>
<li>Detect the source language automatically.</li>
</ul>
</li>
<li><b>Stage 2: Translation & Audio Output</b>
<ul>
<li>Translate text using <b>Gemini Generative AI</b>.</li>
<li>Generate audio using <b>gTTS</b>.</li>
<li>Send the translated text and audio back to the Flutter app for display/playback.</li>
</ul>
</li>
</ol>

<h2 style="font-family: 'Arial Black', sans-serif; color:#1F618D;"> Setup Instructions</h2>

<ul style="font-family: 'Verdana', sans-serif; font-size:16px;">
<li><b>Get API Key:</b> Obtain from <a href="https://console.groq.com/keys">Gemini Console</a> and update <code>.env</code>:
<pre>GEMINI_API_KEY=your_api_key_here</pre></li>

<li><b>Install Dependencies:</b>
<pre>pip install -r requirements.txt</pre>
</li>

<li><b>Run Flask Backend:</b>
<pre>python app.py</pre>
</li>

<li><b>Run Flutter App:</b> Connect to the backend and start translating signboard images.</li>
</ul>

<h2 style="font-family: 'Arial Black', sans-serif; color:#1F618D;"> Features</h2>
<ul style="font-family: 'Verdana', sans-serif; font-size:16px;">
<li> Image-based text extraction (Tesseract OCR)</li>
<li>Multi-language translation (Gemini AI)</li>
<li> Audio output using gTTS</li>
<li> Flutter app integration</li>
<li> Real-time translation and playback</li>
</ul>

<h2 style="font-family: 'Arial Black', sans-serif; color:#1F618D;"> License & Terms</h2>
<p style="font-family: 'Verdana', sans-serif; font-size:16px;">
Copyright (C) Codebasics Inc. All rights reserved.<br>
Licensed under the <b>MIT License</b>.<br>
Commercial use is strictly prohibited without prior written permission.<br>
Attribution must be given in all copies or substantial portions of the software.
</p>






