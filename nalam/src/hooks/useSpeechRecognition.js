import { useState, useRef, useCallback } from 'react';

export const useSpeechRecognition = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [error, setError] = useState(null);
    const recognition = useRef(null);

    const startListening = useCallback(() => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            setError("Speech recognition is not supported in this browser.");
            return;
        }

        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition.current = new SpeechRec();
        recognition.current.continuous = true;
        recognition.current.interimResults = true;
        // Set explicitly to Tamil for optimal native accuracy
        recognition.current.lang = 'ta-IN';

        recognition.current.onstart = () => {
            setIsListening(true);
            setTranscript('');
            setError(null);
        };

        recognition.current.onresult = (event) => {
            let currentTranscript = '';
            for (let i = 0; i < event.results.length; i++) {
                currentTranscript += event.results[i][0].transcript;
            }
            setTranscript(currentTranscript);
        };

        recognition.current.onerror = (event) => {
            console.error("Speech recognition error", event.error);
            setError(event.error === 'not-allowed' ? 'Microphone permission denied' : event.error);
            setIsListening(false);
        };

        recognition.current.onend = () => {
            setIsListening(false);
        };

        try {
            recognition.current.start();
        } catch (e) {
            console.error(e);
        }
    }, []);

    const stopListening = useCallback(() => {
        if (recognition.current) {
            recognition.current.stop();
            setIsListening(false);
        }
    }, []);

    return { isListening, transcript, error, startListening, stopListening };
};
