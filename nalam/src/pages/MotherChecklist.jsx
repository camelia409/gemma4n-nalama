import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getVisits } from '../utils/storage';
import { apiCall } from '../utils/api';
import { speak } from '../utils/audio';
import { useLanguage } from '../context/LanguageContext';

export default function MotherChecklist() {
    const { visitId } = useParams();
    const navigate = useNavigate();
    const { t, lang } = useLanguage();
    const [currentQ, setCurrentQ] = useState(0);
    const [answers, setAnswers] = useState({});
    const [loading, setLoading] = useState(false);

    const questionsList = [
        { id: 'bleeding', text: t.motherQuestions.bleeding },
        { id: 'fever', text: t.motherQuestions.fever },
        { id: 'depressed', text: t.motherQuestions.depressed }
    ];

    useEffect(() => {
        if (currentQ < questionsList.length && lang === 'tamil') {
            speak(questionsList[currentQ].text);
        }
    }, [currentQ, lang]);

    const handleAnswer = async (val) => {
        // YES is a danger sign here!
        const q = questionsList[currentQ];
        const newAnswers = { ...answers, [q.id]: val };
        setAnswers(newAnswers);

        if (currentQ < questionsList.length - 1) {
            setCurrentQ(currentQ + 1);
        } else {
            setLoading(true);

            try {
                const result = await apiCall('/mother-health', { answers: newAnswers });

                // Update LocalStorage directly to append mother_result
                const visits = JSON.parse(localStorage.getItem('nalam_visits')) || [];
                const idx = visits.findIndex(v => v.id === visitId);
                if (idx !== -1) {
                    visits[idx].mother_result = result;
                    localStorage.setItem('nalam_visits', JSON.stringify(visits));
                }
                navigate(`/result/${visitId}`);
            } catch (err) {
                // Offline Fallback for Mother
                const hasDanger = Object.values(newAnswers).some(v => v === true);
                const result = {
                    is_safe: !hasDanger,
                    tamil_message: hasDanger ? "தாய்க்கு ஆபத்து அறிகுறிகள் உள்ளன. உடனடியாக PHC-க்கு செல்லவும்." : "தாய்க்கு எந்த அபாய அறிகுறியும் இல்லை.",
                    english_message: hasDanger ? "Refer mother to PHC immediately." : "Observe mother at home.",
                    danger_signs: hasDanger ? ["தாய் உடல்நலம் (உள்ளூர் முடிவு)"] : [],
                    isFallback: true
                };
                const visits = JSON.parse(localStorage.getItem('nalam_visits')) || [];
                const idx = visits.findIndex(v => v.id === visitId);
                if (idx !== -1) {
                    visits[idx].mother_result = result;
                    localStorage.setItem('nalam_visits', JSON.stringify(visits));
                }
                navigate(`/result/${visitId}`);
            }
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 flex-col">
                <svg className="animate-spin h-12 w-12 text-brand-green mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle></svg>
            </div>
        );
    }

    const q = questionsList[currentQ];

    return (
        <div className="p-6 min-h-screen flex flex-col justify-center bg-gray-50">
            <div className="absolute top-4 left-0 right-0 max-w-[430px] mx-auto text-center font-bold text-gray-500 uppercase tracking-widest text-sm">
                {t.motherTitle}
            </div>

            <div className="mb-6 flex space-x-2 mt-8">
                {questionsList.map((_, i) => (
                    <div key={i} className={`h-2 flex-1 rounded-full ${i <= currentQ ? 'bg-indigo-500' : 'bg-gray-200'}`}></div>
                ))}
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100 flex-1 flex flex-col justify-center items-center text-center">
                <h2 className="text-3xl font-bold text-brand-text mb-12 leading-snug">
                    {q.text}
                </h2>

                <div className="w-full space-y-4">
                    <button
                        onClick={() => handleAnswer(true)}
                        className="w-full h-[80px] bg-red-50 text-brand-red border-2 border-brand-red text-2xl font-bold rounded-2xl shadow-sm active:scale-95 transition-transform"
                    >
                        {t.yes}
                    </button>

                    <button
                        onClick={() => handleAnswer(false)}
                        className="w-full h-[80px] bg-green-50 text-brand-green border-2 border-brand-green text-2xl font-bold rounded-2xl shadow-sm active:scale-95 transition-transform"
                    >
                        {t.no}
                    </button>
                </div>
            </div>
        </div>
    );
}
