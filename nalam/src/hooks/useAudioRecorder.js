import { useState, useRef } from 'react';

export const useAudioRecorder = () => {
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorder = useRef(null);
    const audioChunks = useRef([]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            // Use webm format as specified
            mediaRecorder.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });

            mediaRecorder.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.current.push(event.data);
                }
            };

            mediaRecorder.current.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Error accessing microphone:", err);
            throw err;
        }
    };

    const stopRecording = () => {
        return new Promise((resolve) => {
            if (!mediaRecorder.current) {
                resolve(null);
                return;
            }

            mediaRecorder.current.onstop = () => {
                const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
                audioChunks.current = [];
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    // Send base64 audio without Data-URI prefix
                    const base64AudioMessage = reader.result.split(',')[1];
                    resolve(base64AudioMessage);
                };
            };

            mediaRecorder.current.stop();
            mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
            setIsRecording(false);
        });
    };

    return { isRecording, startRecording, stopRecording };
};
