import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getVisits } from '../utils/storage';
import { speak } from '../utils/audio';
import { useLanguage } from '../context/LanguageContext';

export default function Result() {
    const { visitId } = useParams();
    const navigate = useNavigate();
    const { t, lang } = useLanguage();
    const [visit, setVisit] = useState(null);

    useEffect(() => {
        const allVisits = getVisits();
        const v = allVisits.find(v => v.id === visitId);
        if (v) {
            setVisit(v);
            if (v.result?.tamil_message && lang === 'tamil') {
                speak(v.result.tamil_message);
            }
            setTimeout(() => {
                if (v.mother_result?.tamil_message && lang === 'tamil') {
                    speak(v.mother_result.tamil_message);
                }
            }, 5000);
        }
    }, [visitId, lang]);

    if (!visit || !visit.result || !visit.mother_result) return null;

    const res = visit.result;
    const mRes = visit.mother_result;

    // Entire visit is safe only if BOTH are safe
    const isSafe = res.is_safe && mRes.is_safe;
    const showFallbackWarning = res.isFallback || mRes.isFallback;

    return (
        <div className={`min-h-[120vh] p-6 pb-32 flex flex-col items-center pt-24 text-center ${isSafe ? 'bg-brand-green' : 'bg-brand-red'} transition-colors duration-500 relative`}>

            {showFallbackWarning && (
                <div className="absolute top-4 left-0 right-0 max-w-[430px] mx-auto px-4 z-50">
                    <div className="bg-white text-brand-text p-2 rounded-lg text-sm font-bold shadow-2xl border-b-[4px] border-orange-400">
                        {t.offlineSubtext}
                    </div>
                </div>
            )}

            {isSafe ? (
                <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mb-6 shadow-lg backdrop-blur-sm">
                    <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                </div>
            ) : (
                <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center mb-6 shadow-lg backdrop-blur-sm">
                    <span className="text-5xl text-white font-bold leading-none select-none">⚠️</span>
                </div>
            )}

            <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-md">
                {isSafe ? t.safeResult : t.dangerResult}
            </h1>

            <h2 className="text-xl text-white/90 font-medium mb-8">
                {isSafe && t.safeSubtext}
            </h2>

            <div className="bg-white max-w-sm w-full p-5 rounded-2xl shadow-2xl mb-8 border border-white/40 space-y-4 text-left">
                <div className="p-3 bg-gray-50 rounded-xl">
                    <h3 className="text-xs uppercase font-bold text-gray-500 mb-2">பச்சிளம் குழந்தை (Baby)</h3>
                    <div className="flex items-start">
                        {!res.is_safe && <span className="mr-2 mt-1">🔴</span>}
                        {res.is_safe ? <span className="mr-2 mt-1">🟢</span> : null}
                        <p className="text-lg font-bold text-gray-800 leading-relaxed flex-1">
                            {lang === 'tamil' ? res.tamil_message : (res.english_message || res.tamil_message)}
                        </p>
                    </div>
                </div>

                <div className="p-3 bg-gray-50 rounded-xl">
                    <h3 className="text-xs uppercase font-bold text-gray-500 mb-2">{t.motherTitle}</h3>
                    <div className="flex items-start">
                        {!mRes.is_safe && <span className="mr-2 mt-1">🔴</span>}
                        {mRes.is_safe ? <span className="mr-2 mt-1">🟢</span> : null}
                        <p className="text-lg font-bold text-gray-800 leading-relaxed flex-1">
                            {lang === 'tamil' ? mRes.tamil_message : (mRes.english_message || mRes.tamil_message)}
                        </p>
                    </div>
                </div>
            </div>

            <div className="w-full max-w-sm space-y-4 relative z-10">
                {isSafe ? (
                    <button onClick={() => navigate('/counselling')} className="btn bg-white text-brand-green border-0 shadow-lg text-xl active:bg-gray-100">
                        {t.counselling}
                    </button>
                ) : (
                    <a href="tel:108" className="btn bg-white text-brand-red border-0 shadow-lg text-xl flex items-center justify-center active:bg-gray-100">
                        <span className="mr-2">📞</span> 108
                    </a>
                )}
                <button onClick={() => navigate('/')} className="btn bg-transparent border-2 border-white text-white text-xl active:bg-white/10 transition-colors">
                    {t.home}
                </button>
            </div>
        </div>
    );
}
