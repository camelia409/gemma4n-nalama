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
            try {
                const res = await apiCall('/counselling', {});
                setText(res.tamil_counselling_text || 'தாய்ப்பால் கொடுப்பது மிகவும் முக்கியம். குழந்தையை சுத்தமாக வைத்துக்கொள்ளுங்கள்.');
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
