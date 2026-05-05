export const speak = (text) => {
    if (!('speechSynthesis' in window)) {
        console.warn("Speech Synthesis not supported");
        return;
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ta-IN';
    utterance.rate = 0.8;
    window.speechSynthesis.speak(utterance);
};
