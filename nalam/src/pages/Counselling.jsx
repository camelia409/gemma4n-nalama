import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiCall } from '../utils/api';
import { speak } from '../utils/audio';
import { hasConsent } from '../utils/storage';
import { useLanguage } from '../context/LanguageContext';

export default function Counselling() {
    const navigate = useNavigate();
    const { t, lang } = useLanguage();
    const [text, setText] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchCounselling() {
            const safeFallbackBody = {
                baby: { weight: 'unknown', age_days: 3, premature: false },
                danger_signs: ['unknown'],
                is_safe: false,
                mother_result: {
                    is_safe: false,
                    danger_signs: [],
                    tamil_message: '',
                    english_message: ''
                }
            };

            try {
                let requestBody = safeFallbackBody;
                try {
                    const allVisits = JSON.parse(localStorage.getItem('nalam_visits') || '[]');
                    const allBabies = JSON.parse(localStorage.getItem('nalam_babies') || '[]');
                    const visit = [...allVisits].reverse().find(v => v?.mother_result && v?.result) || null;
                    const baby = visit ? allBabies.find(b => b.id === visit.babyId) : null;

                    if (visit && baby) {
                        const visitDate = new Date(visit.timestamp);
                        const birthDate = new Date(baby.dob);
                        const msPerDay = 1000 * 60 * 60 * 24;
                        let ageDays = Number.isFinite(visitDate.getTime()) && Number.isFinite(birthDate.getTime())
                            ? Math.round((visitDate.getTime() - birthDate.getTime()) / msPerDay)
                            : NaN;

                        if (!Number.isFinite(ageDays)) {
                            ageDays = parseInt(visit.day, 10);
                        }
                        if (!Number.isFinite(ageDays)) {
                            ageDays = 3;
                        }

                        requestBody = {
                            baby: {
                                weight: String(baby.weight ?? 'unknown'),
                                age_days: ageDays,
                                premature: Boolean(baby.premature ?? false)
                            },
                            danger_signs: visit.result?.danger_signs ?? [],
                            is_safe: visit.result?.is_safe ?? false,
                            mother_result: {
                                is_safe: visit.mother_result?.is_safe ?? false,
                                danger_signs: visit.mother_result?.danger_signs ?? [],
                                tamil_message: visit.mother_result?.tamil_message ?? '',
                                english_message: visit.mother_result?.english_message ?? ''
                            }
                        };
                    }
                } catch {
                    requestBody = safeFallbackBody;
                }

                const res = await apiCall('/counselling', { ...requestBody, consent_given: hasConsent() });
                setText(
                    lang === 'tamil'
                        ? (res.tamil_counselling_text || 'தாய்ப்பால் கொடுப்பது மிகவும் முக்கியம். குழந்தையை சுத்தமாக வைத்துக்கொள்ளுங்கள்.')
                        : (res.english_counselling_text || 'Breastfeeding is very important. Keep the baby clean and continue routine newborn care.')
                );
            } catch {
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
