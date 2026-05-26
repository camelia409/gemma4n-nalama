import { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const translations = {
    tamil: {
        appTitle: "நலம்",
        newBaby: "புதிய குழந்தை",
        newVisit: "புதிய வருகை",
        noBabies: "பதிவுகள் இல்லை",
        lastVisit: "கடைசி வருகை: நாள்",
        nextVisit: "அடுத்த வருகை: விரைவில்",
        save: "சேமி",
        babyName: "குழந்தை பெயர்",
        dob: "பிறந்த தேதி",
        weight: "எடை (kg)",
        motherName: "அம்மா பெயர்",
        fatherName: "தந்தை பெயர்",
        village: "கிராமம்",
        phone: "தொலைபேசி",
        premature: "நேரத்திற்கு முன் பிறந்ததா?",
        homeDelivery: "வீட்டில் பிறந்ததா?",
        complications: "பிறக்கும்போது சிக்கல்? (விருப்பமானால்)",
        visitTitle: "வருகை",
        startVisit: "வருகை தொடங்கு",
        visitDay: "வருகை நாள் (Visit Day)",
        day: "நாள்",
        speakInstruction: "அம்மா சொல்வதை பதிவு செய்",
        recording: "பேசவும்...",
        yes: "ஆம்",
        no: "இல்லை",
        safeResult: "வீட்டில் கவனிக்கவும்",
        safeSubtext: "2 நாட்களில் மீண்டும் வருக",
        dangerResult: "உடனே PHC-க்கு அனுப்பவும்",
        counselling: "ஆலோசனை",
        home: "முகப்பு",
        playAudio: "ஒலிக்க கேள்",
        offlineSubtext: "சர்வர் இணைப்பு இல்லை — உள்ளூர் முடிவு பயன்படுத்தப்பட்டது",
        momConcern: "அம்மா இதைப் பற்றி கவலைப்படுகிறார்",
        confirmTitle: "அம்மா சொன்னதை உறுதிசெய்யவும்",
        confirmSubtitle: "உங்கள் கண்களால் எதை பார்த்தீர்கள் என்பதை குறிக்கவும்.",
        motherSaid: "அம்மா சொன்னது:",
        noConcernsSpoken: "அம்மா எந்த கவலையும் சொல்லவில்லை.",
        markNormal: "சரியானது",
        markProblem: "பிரச்சனை",
        addOtherConcern: "வேறு ஏதேனும் கவலை சேர்க்கவும்",
        addOtherConcernPlaceholder: "எ.கா. கையில் சிவப்பு கட்டி, தொப்புள் நாற்றம் வீசுகிறது",
        addBtn: "சேர்",
        continue: "தொடர",
        questions: {
            feeding: "குழந்தை சரியாக பால் குடிக்கிறதா?",
            activity: "குழந்தை சுறுசுறுப்பாக இருக்கிறதா?",
            warmth: "குழந்தை உடல் வெப்பமாக இருக்கிறதா?",
            breathing: "குழந்தை சரியாக மூச்சு விடுகிறதா?"
        },
        motherTitle: "தாய் உடல்நலம் (Mother's Health)",
        motherQuestions: {
            bleeding: "அம்மாக்கு அதிக இரத்தக்கசிவு உள்ளதா?",
            fever: "அம்மாக்கு காய்ச்சல் உள்ளதா?",
            depressed: "அம்மா மிகவும் சோர்வாக அல்லது சங்கடப்பட்டிருக்கிறாரா?"
        }
    },
    english: {
        appTitle: "Nalam",
        newBaby: "New Baby",
        newVisit: "New Visit",
        noBabies: "No records found",
        lastVisit: "Last visit: Day",
        nextVisit: "Next visit: Soon",
        save: "Save",
        babyName: "Baby Name",
        dob: "Date of Birth",
        weight: "Weight (kg)",
        motherName: "Mother's Name",
        fatherName: "Father's Name",
        village: "Village",
        phone: "Phone Number",
        premature: "Born premature?",
        homeDelivery: "Home Delivery?",
        complications: "Birth complications? (Optional)",
        visitTitle: "Visit",
        startVisit: "Start Visit",
        visitDay: "Visit Day",
        day: "Day",
        speakInstruction: "Record mother's concern",
        recording: "Recording...",
        yes: "Yes",
        no: "No",
        safeResult: "Observe at Home",
        safeSubtext: "Return in 2 Days",
        dangerResult: "Refer to PHC immediately",
        counselling: "Counselling",
        home: "Home",
        playAudio: "Listen to Audio",
        offlineSubtext: "Offline - Local Rules Applied",
        momConcern: "Mother is concerned about this",
        confirmTitle: "Confirm what the mother said",
        confirmSubtitle: "Mark anything you observe differently.",
        motherSaid: "Mother said:",
        noConcernsSpoken: "Mother did not mention any concerns.",
        markNormal: "Normal",
        markProblem: "Problem",
        addOtherConcern: "Add any other concern you see",
        addOtherConcernPlaceholder: "e.g. red rash on arm, umbilical cord smells",
        addBtn: "Add",
        continue: "Continue",
        questions: {
            feeding: "Is the baby feeding properly?",
            activity: "Is the baby active and alert?",
            warmth: "Is the baby's body warm?",
            breathing: "Is the baby breathing normally?"
        },
        motherTitle: "Mother's Health Check",
        motherQuestions: {
            bleeding: "Is the mother bleeding heavily?",
            fever: "Does the mother have a fever?",
            depressed: "Is the mother depressed or unusually sad?"
        }
    }
};

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

export const useLanguage = () => useContext(LanguageContext);
