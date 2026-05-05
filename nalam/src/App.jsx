import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useLanguage } from './context/LanguageContext';
import Home from './pages/Home';
import NewBaby from './pages/NewBaby';
import NewVisit from './pages/NewVisit';
import Checklist from './pages/Checklist';
import MotherChecklist from './pages/MotherChecklist';
import Result from './pages/Result';
import Counselling from './pages/Counselling';

const LanguageToggle = () => {
  const { lang, toggleLanguage } = useLanguage();
  return (
    <button onClick={toggleLanguage} className="fixed top-4 right-4 z-[100] bg-white/90 backdrop-blur-md shadow-lg rounded-full px-4 py-2 font-bold text-brand-green border border-brand-green/20 active:scale-95 transition-transform flex items-center justify-center">
      {lang === 'tamil' ? 'EN' : 'தமிழ்'}
    </button>
  )
};

export default function App() {
  return (
    <BrowserRouter>
      <LanguageToggle />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/new-baby" element={<NewBaby />} />
        <Route path="/visit/:babyId" element={<NewVisit />} />
        <Route path="/visit/:babyId/checklist" element={<Checklist />} />
        <Route path="/mother-checklist/:visitId" element={<MotherChecklist />} />
        <Route path="/result/:visitId" element={<Result />} />
        <Route path="/counselling" element={<Counselling />} />
      </Routes>
    </BrowserRouter>
  );
}
