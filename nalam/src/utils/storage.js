const MS_PER_DAY = 86_400_000;

/**
 * Compute the baby's age in days from `dob` (YYYY-MM-DD string).
 * Returns a non-negative integer; safe for missing/invalid input.
 */
export const computeAgeDays = (dob) => {
    if (!dob) return 0;
    const birth = new Date(dob);
    if (Number.isNaN(birth.getTime())) return 0;
    const diff = (Date.now() - birth.getTime()) / MS_PER_DAY;
    return Math.max(0, Math.floor(diff));
};

// ----- Consent ---------------------------------------------------------------
// Persisted once granted. Decliners are only suppressed for the current tab
// session (sessionStorage), so the app can ask again on a future launch.

const CONSENT_KEY = 'nalam_consent_given';
const CONSENT_DISMISSED_KEY = 'nalam_consent_dismissed';

export const hasConsent = () => {
    try {
        const raw = localStorage.getItem(CONSENT_KEY);
        if (!raw) return false;
        return JSON.parse(raw).value === true;
    } catch {
        return false;
    }
};

export const grantConsent = () => {
    localStorage.setItem(CONSENT_KEY, JSON.stringify({
        value: true,
        timestamp: new Date().toISOString(),
    }));
};

// True if a decision is still needed (no grant on file, not dismissed this session).
export const needsConsentDecision = () =>
    !hasConsent() && sessionStorage.getItem(CONSENT_DISMISSED_KEY) !== 'true';

export const dismissConsentForSession = () => {
    sessionStorage.setItem(CONSENT_DISMISSED_KEY, 'true');
};

export const getBabies = () => JSON.parse(localStorage.getItem('nalam_babies') || '[]');

export const saveBaby = (baby) => {
    const babies = getBabies();
    const newBaby = { id: Date.now().toString(), ...baby };
    babies.push(newBaby);
    localStorage.setItem('nalam_babies', JSON.stringify(babies));
    return newBaby;
};

export const getVisits = (babyId) => {
    const allVisits = JSON.parse(localStorage.getItem('nalam_visits') || '[]');
    return babyId ? allVisits.filter(v => v.babyId === babyId) : allVisits;
};

export const saveVisit = (visit) => {
    const visits = JSON.parse(localStorage.getItem('nalam_visits') || '[]');
    const newVisit = { id: Date.now().toString(), timestamp: new Date().toISOString(), ...visit };
    visits.push(newVisit);
    localStorage.setItem('nalam_visits', JSON.stringify(visits));
    return newVisit;
};
