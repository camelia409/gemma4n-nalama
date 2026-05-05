const BASE_URL = ''; // Relative path for Kaggle hosted flask app

export const apiCall = async (endpoint, data) => {
    try {
        const res = await fetch(`${BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('API failed');
        return await res.json();
    } catch (err) {
        console.error(`API Error on ${endpoint}:`, err);
        throw err;
    }
};

export const checkHealth = async () => {
    try {
        const res = await fetch(`${BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'ngrok-skip-browser-warning': 'true'
            }
        });
        return await res.json();
    } catch {
        return { status: 'offline' };
    }
}
