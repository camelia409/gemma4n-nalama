import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiCall } from '../utils/api';
import { useLanguage } from '../context/LanguageContext';

/**
 * Single-page maternal check.
 *   - Three standard items (bleeding / fever / depressed). YES = danger.
 *   - Free-text "other concern" for things outside the list.
 */
export default function MotherChecklist() {
    const { visitId } = useParams();
    const navigate = useNavigate();
    const { t } = useLanguage();
    const [loading, setLoading] = useState(false);

    // All three start False = no danger.
    const [answers, setAnswers] = useState({
        bleeding: false, fever: false, depressed: false,
    });
    const [extraConcerns, setExtraConcerns] = useState([]);
    const [extraDraft, setExtraDraft] = useState('');

    const items = [
        { id: 'bleeding',  text: t.motherQuestions.bleeding },
        { id: 'fever',     text: t.motherQuestions.fever },
        { id: 'depressed', text: t.motherQuestions.depressed },
    ];

    const setItem = (id, hasDanger) => setAnswers(prev => ({ ...prev, [id]: hasDanger }));

    const addExtra = () => {
        const v = extraDraft.trim();
        if (!v) return;
        setExtraConcerns(prev => [...prev, v]);
        setExtraDraft('');
    };
    const removeExtra = (idx) => setExtraConcerns(prev => prev.filter((_, i) => i !== idx));

    const handleSubmit = async () => {
        setLoading(true);

        const persist = (result) => {
            const visits = JSON.parse(localStorage.getItem('nalam_visits')) || [];
            const idx = visits.findIndex(v => v.id === visitId);
            if (idx !== -1) {
                visits[idx].mother_result = result;
                visits[idx].mother_extra_concerns = extraConcerns;
                localStorage.setItem('nalam_visits', JSON.stringify(visits));
            }
        };

        try {
            const result = await apiCall('/mother-health', {
                answers,
                extra_concerns: extraConcerns,
            });
            persist(result);
            navigate(`/result/${visitId}`);
        } catch {
            const hasDanger = Object.values(answers).some(v => v === true) || extraConcerns.length > 0;
            const result = {
                is_safe: !hasDanger,
                tamil_message: hasDanger
                    ? "தாய்க்கு ஆபத்து அறிகுறிகள் உள்ளன. உடனடியாக PHC-க்கு செல்லவும்."
                    : "தாய்க்கு எந்த அபாய அறிகுறியும் இல்லை.",
                english_message: hasDanger
                    ? "Refer mother to PHC immediately."
                    : "Observe mother at home.",
                danger_signs: hasDanger ? [
                    ...Object.entries(answers).filter(([, v]) => v === true).map(([k]) => k),
                    ...extraConcerns,
                ] : [],
                isFallback: true,
            };
            persist(result);
            navigate(`/result/${visitId}`);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50 flex-col">
                <svg className="animate-spin h-12 w-12 text-indigo-500 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle></svg>
            </div>
        );
    }

    return (
        <div className="p-6 pb-32 min-h-screen bg-gray-50">
            <div className="pt-10 pb-4 text-center">
                <p className="text-sm font-bold text-gray-500 uppercase tracking-widest">{t.motherTitle}</p>
                <h1 className="text-2xl font-bold text-brand-text mt-2">{t.confirmTitle}</h1>
                <p className="text-sm text-gray-600 mt-1">{t.confirmSubtitle}</p>
            </div>

            <div className="space-y-3 mb-6">
                {items.map(item => {
                    const hasDanger = answers[item.id] === true;
                    return (
                        <div
                            key={item.id}
                            className={`bg-white p-4 rounded-2xl shadow-sm border-2 ${
                                hasDanger ? 'border-brand-red' : 'border-gray-100'
                            }`}
                        >
                            <p className="text-base font-semibold text-brand-text mb-3">{item.text}</p>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setItem(item.id, false)}
                                    className={`flex-1 py-3 rounded-xl font-bold text-sm transition ${
                                        !hasDanger
                                            ? 'bg-brand-green text-white shadow'
                                            : 'bg-gray-100 text-gray-500'
                                    }`}
                                >
                                    ✓ {t.no}
                                </button>
                                <button
                                    onClick={() => setItem(item.id, true)}
                                    className={`flex-1 py-3 rounded-xl font-bold text-sm transition ${
                                        hasDanger
                                            ? 'bg-brand-red text-white shadow'
                                            : 'bg-gray-100 text-gray-500'
                                    }`}
                                >
                                    ✗ {t.yes}
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 mb-6">
                <p className="text-sm font-bold text-brand-text mb-2">{t.addOtherConcern}</p>
                <div className="flex gap-2 mb-3">
                    <input
                        type="text"
                        value={extraDraft}
                        onChange={e => setExtraDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && addExtra()}
                        placeholder={t.addOtherConcernPlaceholder}
                        className="flex-1 p-3 border rounded-xl bg-gray-50 text-sm text-brand-text outline-none focus:border-indigo-400"
                    />
                    <button
                        onClick={addExtra}
                        disabled={!extraDraft.trim()}
                        className={`px-4 py-3 rounded-xl font-bold text-sm ${
                            extraDraft.trim() ? 'bg-indigo-500 text-white' : 'bg-gray-200 text-gray-400'
                        }`}
                    >
                        + {t.addBtn}
                    </button>
                </div>
                {extraConcerns.length > 0 && (
                    <div className="space-y-2">
                        {extraConcerns.map((c, i) => (
                            <div
                                key={i}
                                className="flex items-center justify-between bg-amber-50 border border-amber-200 p-3 rounded-xl"
                            >
                                <p className="text-sm text-brand-text flex-1">{c}</p>
                                <button onClick={() => removeExtra(i)} className="text-gray-400 text-xl px-2">×</button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-gray-50 via-gray-50 to-transparent max-w-[430px] mx-auto z-10">
                <button
                    onClick={handleSubmit}
                    className="w-full h-[60px] bg-indigo-500 text-white text-lg font-bold rounded-2xl shadow-md active:scale-95 transition-transform"
                >
                    {t.continue} →
                </button>
            </div>
        </div>
    );
}
