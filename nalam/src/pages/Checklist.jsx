import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getBabies, saveVisit } from '../utils/storage';
import { apiCall } from '../utils/api';
import { useLanguage } from '../context/LanguageContext';

/**
 * Confirmation-style checklist:
 *   - Pre-filled from what the mother said (sessionStorage flags from /audio-text)
 *   - ASHA toggles only what she observes differently
 *   - Free-text "other concern" field for anything outside the 4 standard items
 */
export default function Checklist() {
    const { babyId } = useParams();
    const navigate = useNavigate();
    const { t, lang } = useLanguage();
    const [baby, setBaby] = useState(null);
    const [loading, setLoading] = useState(false);

    // Each item starts True = normal. Voice-flagged items start False = problem.
    const [answers, setAnswers] = useState({
        feeding: true, activity: true, warmth: true, breathing: true,
    });
    const [flags, setFlags] = useState({});
    const [transcript, setTranscript] = useState('');
    const [extraConcerns, setExtraConcerns] = useState([]);
    const [extraDraft, setExtraDraft] = useState('');

    const items = [
        { id: 'feeding',   text: t.questions.feeding },
        { id: 'activity',  text: t.questions.activity },
        { id: 'warmth',    text: t.questions.warmth },
        { id: 'breathing', text: t.questions.breathing },
    ];

    useEffect(() => {
        const b = getBabies().find(x => x.id === babyId);
        setBaby(b);

        const storedFlags = sessionStorage.getItem(`flags_${babyId}`);
        const storedTranscript = sessionStorage.getItem(`transcript_${babyId}`) || '';
        setTranscript(storedTranscript);

        if (storedFlags) {
            const parsed = JSON.parse(storedFlags);
            setFlags(parsed);
            // Pre-fill the toggles: voice-flagged items default to "problem"
            setAnswers({
                feeding:   !parsed.feeding,
                activity:  !parsed.activity,
                warmth:    !parsed.warmth,
                breathing: !parsed.breathing,
            });
        }
    }, [babyId]);

    const setItem = (id, normal) => setAnswers(prev => ({ ...prev, [id]: normal }));

    const addExtra = () => {
        const v = extraDraft.trim();
        if (!v) return;
        setExtraConcerns(prev => [...prev, v]);
        setExtraDraft('');
    };

    const removeExtra = (idx) => {
        setExtraConcerns(prev => prev.filter((_, i) => i !== idx));
    };

    const handleSubmit = async () => {
        setLoading(true);

        const visitData = {
            babyId,
            day: '3',
            answers,
            transcript,
            extra_concerns: extraConcerns,
            timestamp: new Date().toISOString(),
        };

        try {
            const result = await apiCall('/assess', {
                baby,
                answers,
                extra_concerns: extraConcerns,
            });
            const saved = saveVisit({ ...visitData, result });
            navigate(`/mother-checklist/${saved.id}`);
        } catch (err) {
            // Offline fallback
            const isSafe = Object.values(answers).every(v => v === true) && extraConcerns.length === 0;
            const result = {
                is_safe: isSafe,
                tamil_message: isSafe
                    ? "வீட்டில் கவனிக்கவும். 2 நாட்களில் மீண்டும் வருக."
                    : "உடனே PHC-க்கு அனுப்பவும்.",
                english_message: isSafe
                    ? "Observe at home. Return in 2 days."
                    : "Refer to PHC immediately.",
                danger_signs: isSafe ? [] : [
                    ...Object.entries(answers).filter(([_, v]) => v === false).map(([k]) => k),
                    ...extraConcerns,
                ],
                isFallback: true,
            };
            const saved = saveVisit({ ...visitData, result });
            navigate(`/mother-checklist/${saved.id}`);
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

    return (
        <div className="p-6 pb-32 min-h-screen bg-gray-50">
            <div className="pt-10 pb-4 text-center">
                <p className="text-sm font-bold text-gray-500 uppercase tracking-widest">பச்சிளம் குழந்தை (Baby)</p>
                <h1 className="text-2xl font-bold text-brand-text mt-2">{t.confirmTitle}</h1>
                <p className="text-sm text-gray-600 mt-1">{t.confirmSubtitle}</p>
            </div>

            {/* Mother's quote, if any */}
            <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 mb-4">
                <p className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">{t.motherSaid}</p>
                {transcript ? (
                    <p className="text-base text-brand-text italic">"{transcript}"</p>
                ) : (
                    <p className="text-base text-gray-400">{t.noConcernsSpoken}</p>
                )}
            </div>

            {/* 4 standard items with pill toggle */}
            <div className="space-y-3 mb-6">
                {items.map(item => {
                    const isProblem = answers[item.id] === false;
                    const flagged = !!flags[item.id];
                    return (
                        <div
                            key={item.id}
                            className={`bg-white p-4 rounded-2xl shadow-sm border-2 ${
                                isProblem ? 'border-brand-red' : 'border-gray-100'
                            }`}
                        >
                            <div className="flex items-start justify-between mb-3">
                                <p className="text-base font-semibold text-brand-text flex-1 pr-2">{item.text}</p>
                                {flagged && <span className="text-xl">⚠️</span>}
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setItem(item.id, true)}
                                    className={`flex-1 py-3 rounded-xl font-bold text-sm transition ${
                                        !isProblem
                                            ? 'bg-brand-green text-white shadow'
                                            : 'bg-gray-100 text-gray-500'
                                    }`}
                                >
                                    ✓ {t.markNormal}
                                </button>
                                <button
                                    onClick={() => setItem(item.id, false)}
                                    className={`flex-1 py-3 rounded-xl font-bold text-sm transition ${
                                        isProblem
                                            ? 'bg-brand-red text-white shadow'
                                            : 'bg-gray-100 text-gray-500'
                                    }`}
                                >
                                    ✗ {t.markProblem}
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Extra concerns input */}
            <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 mb-6">
                <p className="text-sm font-bold text-brand-text mb-2">{t.addOtherConcern}</p>
                <div className="flex gap-2 mb-3">
                    <input
                        type="text"
                        value={extraDraft}
                        onChange={e => setExtraDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && addExtra()}
                        placeholder={t.addOtherConcernPlaceholder}
                        className="flex-1 p-3 border rounded-xl bg-gray-50 text-sm text-brand-text outline-none focus:border-brand-green"
                    />
                    <button
                        onClick={addExtra}
                        disabled={!extraDraft.trim()}
                        className={`px-4 py-3 rounded-xl font-bold text-sm ${
                            extraDraft.trim()
                                ? 'bg-brand-green text-white'
                                : 'bg-gray-200 text-gray-400'
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
                                <button
                                    onClick={() => removeExtra(i)}
                                    className="text-gray-400 text-xl px-2"
                                >×</button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Submit */}
            <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-gray-50 via-gray-50 to-transparent max-w-[430px] mx-auto z-10">
                <button
                    onClick={handleSubmit}
                    className="w-full h-[60px] bg-brand-green text-white text-lg font-bold rounded-2xl shadow-md active:scale-95 transition-transform"
                >
                    {t.continue} →
                </button>
            </div>
        </div>
    );
}
