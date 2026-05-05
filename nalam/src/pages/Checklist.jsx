import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getBabies, saveVisit } from '../utils/storage';
import { apiCall } from '../utils/api';
import { speak } from '../utils/audio';
import { useLanguage } from '../context/LanguageContext';

export default function Checklist() {
    const { babyId } = useParams();
    const navigate = useNavigate();
    const { t, lang } = useLanguage();
    const [currentQ, setCurrentQ] = useState(0);
    const [answers, setAnswers] = useState({});
    const [flags, setFlags] = useState({});
    const [baby, setBaby] = useState(null);
    const [loading, setLoading] = useState(false);

    const questionsList = [
        { id: 'feeding', text: t.questions.feeding },
        { id: 'activity', text: t.questions.activity },
        { id: 'warmth', text: t.questions.warmth },
        { id: 'breathing', text: t.questions.breathing }
    ];

    useEffect(() => {
        const b = getBabies().find(x => x.id === babyId);
        setBaby(b);
        const storedFlags = sessionStorage.getItem(`flags_${babyId}`);
        if (storedFlags) setFlags(JSON.parse(storedFlags));
    }, [babyId]);

    useEffect(() => {
        if (currentQ < questionsList.length && lang === 'tamil') {
            speak(questionsList[currentQ].text);
        }
    }, [currentQ, lang]);

    const handleAnswer = async (val) => {
        const q = questionsList[currentQ];
        const newAnswers = { ...answers, [q.id]: val };
        setAnswers(newAnswers);

        if (currentQ < questionsList.length - 1) {
            setCurrentQ(currentQ + 1);
        } else {
            setLoading(true);

            // Clinical Safety Override: If Gemma detected a danger in the audio transcription,
            // it physically overrides human-error regardless of what the ASHA clicked.
            const finalAnswers = { ...newAnswers };
            if (flags.feeding) finalAnswers.feeding = false;
            if (flags.activity) finalAnswers.activity = false;
            if (flags.warmth) finalAnswers.warmth = false;
            if (flags.breathing) finalAnswers.breathing = false;

            const visitData = { babyId, day: '3', answers: finalAnswers, timestamp: new Date().toISOString() };

            try {
                const result = await apiCall('/assess', { baby, answers: finalAnswers });
                const saved = saveVisit({ ...visitData, result });
                navigate(`/mother-checklist/${saved.id}`);
            } catch (err) {
                // Offline Fallback logic
                const isSafe = Object.values(finalAnswers).every(v => v === true);
                const result = {
                    is_safe: isSafe,
                    tamil_message: isSafe ? "வீட்டில் கவனிக்கவும். 2 நாட்களில் மீண்டும் வருக." : "உடனே PHC-க்கு அனுப்பவும்.",
                    english_message: isSafe ? "Observe at home. Return in 2 days." : "Refer to PHC immediately.",
                    danger_signs: isSafe ? [] : ["அபாய அறிகுறிகள் உள்ளன (உள்ளூர் முடிவு)"],
                    isFallback: true
                };
                const saved = saveVisit({ ...visitData, result });
                navigate(`/mother-checklist/${saved.id}`);
            }
        }
    };

    if (!baby) return null;

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 flex-col">
                <svg className="animate-spin h-12 w-12 text-brand-green mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle></svg>
            </div>
        );
    }

    const q = questionsList[currentQ];
    const hasFlag = flags[q?.id];

    return (
        <div className="p-6 min-h-screen flex flex-col justify-center">
            <div className="absolute top-4 left-0 right-0 max-w-[430px] mx-auto text-center font-bold text-gray-500 uppercase tracking-widest text-sm">
                பச்சிளம் குழந்தை (Baby)
            </div>

            <div className="mb-6 flex space-x-2">
                {questionsList.map((_, i) => (
                    <div key={i} className={`h-2 flex-1 rounded-full ${i <= currentQ ? 'bg-brand-green' : 'bg-gray-200'}`}></div>
                ))}
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100 flex-1 flex flex-col justify-center items-center text-center">
                {hasFlag && (
                    <div className="bg-brand-yellow/20 text-yellow-800 p-3 rounded-lg mb-6 w-full font-bold flex items-center justify-center shadow-sm">
                        <span className="mr-2">⚠️</span> {t.momConcern}
                    </div>
                )}

                <h2 className="text-3xl font-bold text-brand-text mb-12 leading-snug">
                    {q.text}
                </h2>

                <div className="w-full space-y-4">
                    <button
                        onClick={() => handleAnswer(true)}
                        className="w-full h-[80px] bg-brand-green text-white text-2xl font-bold rounded-2xl shadow-md active:scale-95 transition-transform"
                    >
                        {t.yes}
                    </button>

                    <button
                        onClick={() => handleAnswer(false)}
                        className="w-full h-[80px] bg-brand-red text-white text-2xl font-bold rounded-2xl shadow-md active:scale-95 transition-transform"
                    >
                        {t.no}
                    </button>
                </div>
            </div>
        </div>
    );
}
