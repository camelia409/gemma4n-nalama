import { useLanguage } from '../context/LanguageContext';

/**
 * One-time, full-screen consent overlay.
 * Shown before any visit flow when no consent decision is on file.
 *  - onAgree:   persist consent (logging enabled) and dismiss
 *  - onDecline: dismiss for this session only (logging stays suppressed)
 * Always shows BOTH Tamil and English so low-literacy workers can read either.
 */
export default function ConsentScreen({ onAgree, onDecline }) {
    const { t } = useLanguage();
    const c = t.consent;

    return (
        <div className="fixed inset-0 z-[200] bg-black/50 backdrop-blur-sm flex items-end sm:items-center justify-center p-4">
            <div className="bg-white w-full max-w-[430px] rounded-3xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto">
                <div className="w-14 h-14 bg-brand-green/10 rounded-2xl flex items-center justify-center mb-4 mx-auto">
                    <span className="text-3xl">🔒</span>
                </div>

                <h2 className="text-2xl font-bold text-brand-text text-center mb-4">
                    {c.title}
                </h2>

                <p className="text-base text-gray-700 leading-relaxed mb-5">
                    {c.body}
                </p>

                <div className="space-y-3">
                    <button
                        onClick={onAgree}
                        className="w-full h-[56px] bg-brand-green text-white text-lg font-bold rounded-2xl shadow-md active:scale-95 transition-transform"
                    >
                        {c.agree}
                    </button>
                    <button
                        onClick={onDecline}
                        className="w-full h-[52px] bg-gray-100 text-gray-600 text-base font-semibold rounded-2xl active:scale-95 transition-transform"
                    >
                        {c.decline}
                    </button>
                </div>
            </div>
        </div>
    );
}
