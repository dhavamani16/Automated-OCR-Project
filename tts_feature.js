
function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}
function pcmToWav(pcm16, sampleRate) {
    const numChannels = 1;
    const bytesPerSample = 2;
    const blockAlign = numChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = pcm16.length * bytesPerSample;
    const apiKey = ""; 
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${API_MODEL}:generateContent?key=${apiKey}`;
    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);
    let offset = 0;
    writeString(view, offset, 'RIFF'); offset += 4;
    view.setUint32(offset, 36 + dataSize, true); offset += 4;
    writeString(view, offset, 'WAVE'); offset += 4;

   
    writeString(view, offset, 'fmt '); offset += 4;
    view.setUint32(offset, 16, true); offset += 4; 
    view.setUint16(offset, 1, true); offset += 2;  
    view.setUint16(offset, numChannels, true); offset += 2; 
    view.setUint32(offset, sampleRate, true); offset += 4; 
    view.setUint32(offset, byteRate, true); offset += 4; 
    view.setUint16(offset, blockAlign, true); offset += 2; 
    view.setUint16(offset, 16, true); offset += 2; 
    writeString(view, offset, 'data'); offset += 4;
    view.setUint32(offset, dataSize, true); offset += 4;
    for (let i = 0; i < pcm16.length; i++, offset += 2) {
        view.setInt16(offset, pcm16[i], true);
    }

    return new Blob([view], { type: 'audio/wav' });
}
async function speakTranslation() {
    if (!lastTranslationText || lastTranslationText.trim() === "") return

    try {
        const voiceName = "Puck"; 
        
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
        const response = await fetch(ttsApiUrl, { /* ... */ }); 
        
        if (!response.ok) { throw new Error(`TTS HTTP error! Status: ${response.status}`); }

        const result = await response.json();
        const part = result?.candidates?.[0]?.content?.parts?.[0];
        const audioData = part?.inlineData?.data;
        const mimeType = part?.inlineData?.mimeType;

        if (audioData && mimeType && mimeType.startsWith("audio/L16")) {
            const sampleRateMatch = mimeType.match(/rate=(\d+)/);
            const sampleRate = parseInt(sampleRateMatch[1], 10);
            
            const pcmData = base64ToArrayBuffer(audioData);
            const pcm16 = new Int16Array(pcmData);
            const wavBlob = pcmToWav(pcm16, sampleRate);
            const audioUrl = URL.createObjectURL(wavBlob);
            const audio = new Audio(audioUrl);
            audio.play();
            audio.onended = () => { URL.revokeObjectURL(audioUrl);  };
            
        } else {
            throw new Error("Invalid or missing audio data in TTS response.");
        }

    } catch (error) {
    
    } finally {
        
    }
}
