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
