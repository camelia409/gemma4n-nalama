import { useState } from 'react';
import { LanguageContext, translations } from './LanguageContext';

export const LanguageProvider = ({ children }) => {
    const [lang, setLang] = useState(() => {
        return localStorage.getItem('nalam_lang') || 'tamil';
    });

    const toggleLanguage = () => {
        const newLang = lang === 'tamil' ? 'english' : 'tamil';
        setLang(newLang);
        localStorage.setItem('nalam_lang', newLang);
    };

    const t = translations[lang];

    return (
        <LanguageContext.Provider value={{ lang, toggleLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
};
