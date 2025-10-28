// --- Utility Functions for Audio Conversion ---

// 1. Helper to write strings (like 'RIFF', 'WAVE') into the DataView for the WAV header
function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

// 2. Converts raw 16-bit PCM audio data (from the API) into a playable WAV Blob.
function pcmToWav(pcm16, sampleRate) {
    const numChannels = 1;
    const bytesPerSample = 2;
    const blockAlign = numChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = pcm16.length * bytesPerSample;
    const apiKey = ""; // Canvas will provide this key at runtime
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${API_MODEL}:generateContent?key=${apiKey}`;
    
    // Create the buffer for the entire WAV file (44 bytes for header + data size)
    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);
    let offset = 0;

    // RIFF Chunk (Standard WAV File Header)
    writeString(view, offset, 'RIFF'); offset += 4;
    view.setUint32(offset, 36 + dataSize, true); offset += 4;
    writeString(view, offset, 'WAVE'); offset += 4;

    // 'fmt ' Chunk (Format description)
    writeString(view, offset, 'fmt '); offset += 4;
    view.setUint32(offset, 16, true); offset += 4; // Sub-chunk size
    view.setUint16(offset, 1, true); offset += 2;  // Audio format (1 for PCM)
    view.setUint16(offset, numChannels, true); offset += 2; // Channels
    view.setUint32(offset, sampleRate, true); offset += 4; // Sample rate
    view.setUint32(offset, byteRate, true); offset += 4; // Byte rate
    view.setUint16(offset, blockAlign, true); offset += 2; // Block align
    view.setUint16(offset, 16, true); offset += 2; // Bits per sample (16-bit)

    // 'data' Chunk (The actual audio data)
    writeString(view, offset, 'data'); offset += 4;
    view.setUint32(offset, dataSize, true); offset += 4;
    
    // Write the actual 16-bit PCM audio data
    for (let i = 0; i < pcm16.length; i++, offset += 2) {
        view.setInt16(offset, pcm16[i], true);
    }

    return new Blob([view], { type: 'audio/wav' });
}


// --- Core Text-to-Speech Function ---
async function speakTranslation() {
    if (!lastTranslationText || lastTranslationText.trim() === "") return;

    // UI state changes (loading indicator, disabling button) omitted for brevity...

    try {
        const voiceName = "Puck"; // Using the "Upbeat" voice
        
        const payload = {
            contents: [{ parts: [{ text: `Say in a clear voice: ${lastTranslationText}` }] }],
            generationConfig: {
                responseModalities: ["AUDIO"],
                speechConfig: {
                    voiceConfig: {
                        prebuiltVoiceConfig: { voiceName: voiceName }
                    }
                }
            },
            model: "gemini-2.5-flash-preview-tts"
        };

        // Network request with exponential backoff omitted for brevity...
        const response = await fetch(ttsApiUrl, { /* ... */ }); 
        
        if (!response.ok) { throw new Error(`TTS HTTP error! Status: ${response.status}`); }

        const result = await response.json();
        const part = result?.candidates?.[0]?.content?.parts?.[0];
        const audioData = part?.inlineData?.data;
        const mimeType = part?.inlineData?.mimeType;

        if (audioData && mimeType && mimeType.startsWith("audio/L16")) {
            // 1. Extract sample rate from the MIME type string (e.g., audio/L16; rate=24000)
            const sampleRateMatch = mimeType.match(/rate=(\d+)/);
            const sampleRate = parseInt(sampleRateMatch[1], 10);
            
            // 2. Convert base64 audio string to raw ArrayBuffer bytes
            const pcmData = base64ToArrayBuffer(audioData);
            // 3. Interpret bytes as 16-bit integers
            const pcm16 = new Int16Array(pcmData);
            
            // 4. Wrap the raw PCM data in a WAV container (using pcmToWav function)
            const wavBlob = pcmToWav(pcm16, sampleRate);
            
            // 5. Create a temporary URL and play the audio
            const audioUrl = URL.createObjectURL(wavBlob);
            const audio = new Audio(audioUrl);
            audio.play();

            // Clean up when done
            audio.onended = () => { URL.revokeObjectURL(audioUrl); /* ... UI reset ... */ };
            
        } else {
            throw new Error("Invalid or missing audio data in TTS response.");
        }

    } catch (error) {
        // Error handling omitted for brevity...
    } finally {
        // UI reset omitted for brevity...
    }
}
