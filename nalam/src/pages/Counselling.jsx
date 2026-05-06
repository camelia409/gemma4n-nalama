import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiCall } from '../utils/api';
import { speak } from '../utils/audio';
import { useLanguage } from '../context/LanguageContext';

export default function Counselling() {
    const navigate = useNavigate();
    const { t, lang } = useLanguage();
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchCounselling() {
            const safeFallbackBody = { // ADDED
                baby: { weight: 'unknown', age_days: 3, premature: false }, // ADDED
                danger_signs: ['unknown'], // ADDED
                is_safe: false, // ADDED
                mother_result: { // ADDED
                    is_safe: false, // ADDED
                    danger_signs: [], // ADDED
                    tamil_message: '', // ADDED
                    english_message: '' // ADDED
                } // ADDED
            }; // ADDED

            try {
                let requestBody = safeFallbackBody; // ADDED
                try { // ADDED
                    const allVisits = JSON.parse(localStorage.getItem('nalam_visits') || '[]'); // ADDED
                    const allBabies = JSON.parse(localStorage.getItem('nalam_babies') || '[]'); // ADDED
                    const visit = [...allVisits].reverse().find(v => v?.mother_result && v?.result) || null; // ADDED
                    const baby = visit ? allBabies.find(b => b.id === visit.babyId) : null; // ADDED

                    if (visit && baby) { // ADDED
                        const visitDate = new Date(visit.timestamp); // ADDED
                        const birthDate = new Date(baby.dateOfBirth); // ADDED
                        const msPerDay = 1000 * 60 * 60 * 24; // ADDED
                        let ageDays = Number.isFinite(visitDate.getTime()) && Number.isFinite(birthDate.getTime()) // ADDED
                            ? Math.round((visitDate.getTime() - birthDate.getTime()) / msPerDay) // ADDED
                            : NaN; // ADDED

                        if (!Number.isFinite(ageDays)) { // ADDED
                            ageDays = parseInt(visit.day, 10); // ADDED
                        } // ADDED
                        if (!Number.isFinite(ageDays)) { // ADDED
                            ageDays = 3; // ADDED
                        } // ADDED

                        requestBody = { // ADDED
                            baby: { // ADDED
                                weight: String(baby.weight ?? 'unknown'), // ADDED
                                age_days: ageDays, // ADDED
                                premature: Boolean(baby.premature ?? false) // ADDED
                            }, // ADDED
                            danger_signs: visit.result?.danger_signs ?? [], // ADDED
                            is_safe: visit.result?.is_safe ?? false, // ADDED
                            mother_result: { // ADDED
                                is_safe: visit.mother_result?.is_safe ?? false, // ADDED
                                danger_signs: visit.mother_result?.danger_signs ?? [], // ADDED
                                tamil_message: visit.mother_result?.tamil_message ?? '', // ADDED
                                english_message: visit.mother_result?.english_message ?? '' // ADDED
                            } // ADDED
                        }; // ADDED
                    } // ADDED
                } catch (storageErr) { // ADDED
                    requestBody = safeFallbackBody; // ADDED
                } // ADDED

                const res = await apiCall('/counselling', requestBody); // CHANGED
                setText( // CHANGED
                    lang === 'tamil' // ADDED
                        ? (res.tamil_counselling_text || 'தாய்ப்பால் கொடுப்பது மிகவும் முக்கியம். குழந்தையை சுத்தமாக வைத்துக்கொள்ளுங்கள்.') // CHANGED
                        : (res.english_counselling_text || 'Breastfeeding is very important. Keep the baby clean and continue routine newborn care.') // ADDED
                ); // ADDED
            } catch (err) {
                setText(lang === 'tamil' ? 'சர்வர் இணைப்பு இல்லை - தயவுசெய்து பொதுவான ஆலோசனைகளை வழங்கவும்.' : 'Offline mode - Please provide general counselling guidelines based on WHO book.');
            }
            setLoading(false);
        }
        fetchCounselling();
    }, [lang]);

    const handlePlay = () => {
        if (lang === 'tamil') speak(text);
    };

    return (
        <div className="p-6 min-h-screen">
            <div className="flex items-center mb-8 mt-4">
                <button onClick={() => navigate(-1)} className="text-brand-green font-bold text-xl mr-4 active:scale-95">←</button>
                <h1 className="text-2xl font-bold text-brand-text">{t.counselling}</h1>
            </div>

            {loading ? (
                <div className="flex justify-center p-12">
                    <svg className="animate-spin h-10 w-10 text-brand-green" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle></svg>
                </div>
            ) : (
                <div className="bg-white p-6 rounded-2xl shadow-md border border-gray-100 mb-8">
                    <p className="text-lg text-gray-800 leading-relaxed font-medium mb-6">
                        {text}
                    </p>
                    <button
                        onClick={handlePlay}
                        className="flex items-center justify-center w-full p-4 bg-brand-green/10 text-brand-green rounded-xl font-bold active:scale-[0.98] transition-transform text-lg"
                    >
                        <span className="mr-2">▶️</span> {t.playAudio}
                    </button>
                </div>
            )}

            <div className="fixed bottom-0 left-0 right-0 p-5 bg-gradient-to-t from-gray-50 via-white to-transparent max-w-[430px] mx-auto pb-8 z-10">
                <button onClick={() => navigate('/')} className="btn btn-outline bg-white/90 backdrop-blur-sm shadow-sm">
                    {t.home}
                </button>
            </div>
        </div>
    );
}
