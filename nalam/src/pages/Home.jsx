import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getBabies, getVisits } from '../utils/storage';
import { useLanguage } from '../context/LanguageContext';

export default function Home() {
    const navigate = useNavigate();
    const [babies, setBabies] = useState([]);
    const { t } = useLanguage();

    useEffect(() => {
        const allBabies = getBabies();
        const enrichedBabies = allBabies.map(baby => {
            const visits = getVisits(baby.id);
            const lastVisit = visits.length ? visits[visits.length - 1] : null;

            return {
                ...baby,
                lastVisitDay: lastVisit ? lastVisit.day : '-',
                isOverdue: false
            };
        });
        setBabies(enrichedBabies);
    }, []);

    return (
        <div className="pb-36 p-6 min-h-screen relative">
            <h1 className="text-4xl font-bold text-brand-green mb-8 text-center mt-6">{t.appTitle}</h1>

            <div className="space-y-4">
                {babies.length === 0 ? (
                    <div className="text-center p-8 bg-white rounded-xl shadow-sm border border-gray-100">
                        <p className="text-gray-500 font-medium">{t.noBabies}</p>
                    </div>
                ) : (
                    babies.map(baby => (
                        <div
                            key={baby.id}
                            className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 border-l-4 border-l-brand-green flex justify-between items-center cursor-pointer active:scale-[0.98] transition-all"
                            onClick={() => navigate(`/visit/${baby.id}`)}
                        >
                            <div>
                                <h3 className="font-bold text-xl text-brand-text mb-1">{baby.name}</h3>
                                <p className="text-sm text-gray-500 font-medium">{t.lastVisit} {baby.lastVisitDay}</p>
                                <p className="text-sm text-gray-500 font-medium">{t.nextVisit}</p>
                            </div>
                            <div className={`w-4 h-4 rounded-full ${baby.isOverdue ? 'bg-brand-red animate-pulse' : 'bg-brand-green'} shadow-sm`}></div>
                        </div>
                    ))
                )}
            </div>

            <div className="pt-6 text-center text-gray-400">
                <p className="text-xs">இது ஒரு முடிவு-ஆதரவு கருவி. இறுதி மருத்துவ தீர்ப்பு சுகாதார நிபுணரிடம் உள்ளது.</p>
                <p className="text-xs">This is a decision-support tool. Final clinical judgment belongs to the healthcare professional.</p>
            </div>

            <div className="fixed bottom-0 left-0 right-0 p-5 bg-gradient-to-t from-gray-50 via-white to-transparent max-w-[430px] mx-auto space-y-3 pb-8 z-10">
                <button onClick={() => navigate('/new-baby')} className="btn btn-primary drop-shadow-md">
                    {t.newBaby}
                </button>
                <button className="btn btn-outline bg-white/80 backdrop-blur-sm">
                    {t.newVisit}
                </button>
            </div>
        </div>
    );
}
