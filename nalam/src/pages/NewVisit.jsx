import { useState, useEffect, useRef } from 'react'; // CHANGED
import { useParams, useNavigate } from 'react-router-dom';
import { getBabies } from '../utils/storage';
import { apiCall } from '../utils/api';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { useLanguage } from '../context/LanguageContext';

export default function NewVisit() {
    const { babyId } = useParams();
    const navigate = useNavigate();
    const { t } = useLanguage();
    const [baby, setBaby] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [showTypedFallback, setShowTypedFallback] = useState(false); // ADDED
    const [typedText, setTypedText] = useState(''); // ADDED
    const [fallbackStatus, setFallbackStatus] = useState(''); // ADDED
    const { isListening, transcript, error, startListening, stopListening } = useSpeechRecognition();
    const recognitionTimeoutRef = useRef(null); // ADDED
    const transcriptRef = useRef(''); // ADDED

    useEffect(() => {
        const b = getBabies().find(x => x.id === babyId);
        setBaby(b);
    }, [babyId]);

    useEffect(() => { // ADDED
        transcriptRef.current = transcript; // ADDED
    }, [transcript]); // ADDED

    useEffect(() => { // ADDED
        return () => { // ADDED
            if (recognitionTimeoutRef.current) { // ADDED
                clearTimeout(recognitionTimeoutRef.current); // ADDED
                recognitionTimeoutRef.current = null; // ADDED
            } // ADDED
        }; // ADDED
    }, []); // ADDED

    if (!baby) return null;

    const submitConcernText = async (inputText) => { // ADDED
        const finalText = (inputText || '').trim(); // ADDED
        if (!finalText) return; // ADDED
        setProcessing(true); // ADDED
        try { // ADDED
            const res = await apiCall('/audio-text', { // ADDED
                text: finalText, // ADDED
                baby_context: { visit_day: 3, birth_weight: baby.weight } // ADDED
            }); // ADDED

            if (!res.error && !res.parse_error) { // ADDED
                const flags = {}; // ADDED
                if (res.feeding_concern) flags.feeding = true; // ADDED
                if (res.activity_concern) flags.activity = true; // ADDED
                if (res.warmth_concern) flags.warmth = true; // ADDED
                if (res.breathing_concern) flags.breathing = true; // ADDED
                sessionStorage.setItem(`flags_${babyId}`, JSON.stringify(flags)); // ADDED
            } // ADDED
        } catch (err) { // ADDED
            console.log("Offline or API Error:", err); // ADDED
        } // ADDED
        setProcessing(false); // ADDED
    }; // ADDED

    const handleTypedSubmit = async () => { // ADDED
        await submitConcernText(typedText); // ADDED
    }; // ADDED

    const handleRecordToggle = async () => {
        if (isListening) {
            if (recognitionTimeoutRef.current) { // ADDED
                clearTimeout(recognitionTimeoutRef.current); // ADDED
                recognitionTimeoutRef.current = null; // ADDED
            } // ADDED
            stopListening();

            // Artificial delay to let final transcription result settle
            setTimeout(async () => {
                const latestTranscript = (transcriptRef.current || '').trim(); // ADDED
                if (latestTranscript.length > 0) { // CHANGED
                    setShowTypedFallback(false); // ADDED
                    setFallbackStatus(''); // ADDED
                    await submitConcernText(latestTranscript); // CHANGED
                } else { // ADDED
                    setShowTypedFallback(true); // ADDED
                }
            }, 500);

        } else {
            setShowTypedFallback(false); // ADDED
            setFallbackStatus(''); // ADDED
            startListening();
            if (recognitionTimeoutRef.current) { // ADDED
                clearTimeout(recognitionTimeoutRef.current); // ADDED
            } // ADDED
            recognitionTimeoutRef.current = setTimeout(() => { // ADDED
                const latestTranscript = (transcriptRef.current || '').trim(); // ADDED
                if (latestTranscript.length === 0) { // ADDED
                    stopListening(); // ADDED
                    setShowTypedFallback(true); // ADDED
                    setFallbackStatus('குரல் பதிவு கிடைக்கவில்லை. தயவுசெய்து உங்கள் கவலையை টাইப் செய்யவும்.\nNo speech transcript received. Please type the mother\'s concern.'); // ADDED
                } // ADDED
                recognitionTimeoutRef.current = null; // ADDED
            }, 8000); // ADDED
        }
    };

    const skipToChecklist = () => {
        navigate(`/visit/${babyId}/checklist`);
    };

    return (
        <div className="p-6 min-h-screen bg-gray-50 flex flex-col justify-center items-center">
            <div className="w-full max-w-sm bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-8">
                <h2 className="text-2xl font-bold text-gray-800">{baby.name}</h2>
                <p className="text-gray-500">{t.visitDay}</p>
                <select className="mt-2 w-full p-3 border rounded-xl bg-gray-50 text-lg font-medium text-gray-700 outline-none">
                    <option>Day 3</option>
                    <option>Day 7</option>
                    <option>Day 14</option>
                </select>
            </div>

            <button
                onClick={handleRecordToggle}
                disabled={processing}
                className={`w-48 h-48 rounded-full flex items-center justify-center mb-8 shadow-xl transition-all duration-300 relative border-[8px]
          ${isListening ? 'bg-red-50 border-red-200 ripple' : 'bg-brand-green border-green-700/20 active:scale-95'}
          ${processing ? 'opacity-50 cursor-not-allowed' : ''}
        `}
            >
                {isListening ? (
                    <div className="w-16 h-16 bg-red-500 rounded-full animate-pulse shadow-lg shadow-red-500/50"></div>
                ) : processing ? (
                    <svg className="animate-spin h-16 w-16 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                ) : (
                    <svg className="w-20 h-20 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>
                )}
            </button>

            {showTypedFallback && ( // ADDED
                <div className="w-full max-w-sm mb-6">{/* ADDED */}
                    <p className="text-sm font-semibold text-brand-text mb-1">அம்மாவின் கவலையை கீழே টাইப் செய்யவும்.</p> {/* ADDED */} 
                    <p className="text-sm text-gray-600 mb-3">Please type the mother's concern below.</p> {/* ADDED */} 
                    {fallbackStatus ? ( // ADDED
                        <p className="text-sm text-red-500 font-medium whitespace-pre-line mb-3">{fallbackStatus}</p> /* ADDED */
                    ) : null} {/* ADDED */} 
                    <textarea /* ADDED */
                        value={typedText} // ADDED
                        onChange={(e) => setTypedText(e.target.value)} // ADDED
                        rows={4} // ADDED
                        className="w-full p-3 border rounded-xl bg-white text-gray-800 outline-none mb-3" // ADDED
                        placeholder="அம்மாவின் கவலை என்ன? / What is the mother's concern?" // ADDED
                    /> {/* ADDED */}
                    <button /* ADDED */
                        onClick={handleTypedSubmit} // ADDED
                        disabled={processing || typedText.trim().length === 0} // ADDED
                        className={`w-full p-3 rounded-xl font-bold text-white ${processing || typedText.trim().length === 0 ? 'bg-gray-400 cursor-not-allowed' : 'bg-brand-green active:bg-green-700'} transition`} // ADDED
                    > {/* ADDED */}
                        உரையை சமர்ப்பிக்கவும் / Submit typed concern {/* ADDED */}
                    </button> {/* ADDED */}
                </div> {/* ADDED */}
            )} // ADDED

            <h3 className="text-xl font-bold text-brand-text mb-6">
                {isListening ? t.recording : processing ? "AI Processing..." : t.speakInstruction}
            </h3>

            <div className="w-full max-w-sm min-h-[100px] p-4 bg-white border rounded-xl mb-8 flex items-center justify-center text-center shadow-sm relative italic text-gray-600">
                {error ? (
                    <span className="text-red-500 font-bold">{error}</span>
                ) : transcript ? (
                    transcript
                ) : (
                    <span className="text-gray-300">...</span>
                )}
            </div>

            <button onClick={skipToChecklist} className="w-full max-w-sm p-4 bg-brand-green text-white text-xl font-bold rounded-xl shadow-md active:bg-green-700 transition">
                {t.startVisit}
            </button>
        </div>
    );
}
