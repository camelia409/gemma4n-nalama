import { useEffect, useState } from 'react';

// VITE_API_URL is set in .env (dev) and in the Vercel dashboard (prod).
// Falls back to '' so the app still works when frontend and backend share an origin.
const BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

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
};

export const useConnectionStatus = () => {
    const [connectionStatus, setConnectionStatus] = useState('checking');

    useEffect(() => {
        let mounted = true;

        const runHealthCheck = async () => {
            try {
                const health = await checkHealth();
                if (!mounted) return;
                if (health?.status && health.status !== 'offline') {
                    setConnectionStatus('connected');
                } else {
                    setConnectionStatus('offline');
                }
            } catch {
                if (!mounted) return;
                setConnectionStatus('offline');
            }
        };

        runHealthCheck();
        const intervalId = setInterval(runHealthCheck, 30000);

        return () => {
            mounted = false;
            clearInterval(intervalId);
        };
    }, []);

    return connectionStatus;
};
