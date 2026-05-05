import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { saveBaby } from '../utils/storage';
import { useLanguage } from '../context/LanguageContext';

export default function NewBaby() {
    const navigate = useNavigate();
    const { t } = useLanguage();
    const [formData, setFormData] = useState({
        name: '',
        dob: '',
        weight: '',
        motherName: '',
        fatherName: '',
        village: '',
        phone: '',
        premature: false,
        homeDelivery: false,
        complications: ''
    });

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        saveBaby(formData);
        navigate('/');
    };

    return (
        <div className="p-6 pb-24 min-h-screen">
            <div className="flex items-center mb-6 mt-4">
                <button onClick={() => navigate(-1)} className="text-brand-green font-bold text-xl mr-4 active:scale-95">←</button>
                <h1 className="text-2xl font-bold text-brand-text">{t.newBaby}</h1>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">{t.babyName}</label>
                    <input required type="text" name="name" onChange={handleChange} className="input-field" />
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">{t.dob}</label>
                    <input required type="date" name="dob" onChange={handleChange} className="input-field" />
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">{t.weight}</label>
                    <input required type="number" step="0.1" name="weight" onChange={handleChange} className="input-field" placeholder="3.2" />
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">{t.motherName}</label>
                    <input required type="text" name="motherName" onChange={handleChange} className="input-field" />
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">{t.fatherName}</label>
                    <input required type="text" name="fatherName" onChange={handleChange} className="input-field" />
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">{t.village}</label>
                    <input required type="text" name="village" onChange={handleChange} className="input-field" />
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1">{t.phone}</label>
                    <input required type="tel" name="phone" onChange={handleChange} className="input-field" />
                </div>

                <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-4">
                    <label className="flex items-center justify-between cursor-pointer">
                        <span className="font-semibold text-brand-text">{t.premature}</span>
                        <input type="checkbox" name="premature" onChange={handleChange} className="w-6 h-6 accent-brand-green" />
                    </label>

                    <label className="flex items-center justify-between cursor-pointer">
                        <span className="font-semibold text-brand-text">{t.homeDelivery}</span>
                        <input type="checkbox" name="homeDelivery" onChange={handleChange} className="w-6 h-6 accent-brand-green" />
                    </label>
                </div>

                <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-1 mt-2">{t.complications}</label>
                    <textarea name="complications" onChange={handleChange} className="input-field" rows="2"></textarea>
                </div>

                <div className="fixed bottom-0 left-0 right-0 p-5 bg-gradient-to-t from-gray-50 via-white to-transparent max-w-[430px] mx-auto pb-8 z-10">
                    <button type="submit" className="btn btn-primary drop-shadow-md">{t.save}</button>
                </div>
            </form>
        </div>
    );
}
