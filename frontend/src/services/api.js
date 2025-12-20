/**
 * Servicio API para el Geovisor de Costos Forestales.
 * Gestiona las llamadas al backend Django.
 */

import axios from 'axios';

// Base URL del backend Django
// En producción usa relative path ('/api') para evitar problemas de CORS/Mixed Content
// En desarrollo, Vite proxy redirige '/api' a localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Obtiene la lista de distritos disponibles.
 */
export const getDistritos = async () => {
    const response = await api.get('/distritos/');
    return response.data;
};

/**
 * Obtiene la lista de cultivos disponibles.
 * @param {string} distritoId - (Opcional) Filtrar por distrito
 */
export const getCultivos = async (distritoId = null) => {
    const params = distritoId ? { distrito: distritoId } : {};
    const response = await api.get('/cultivos/', { params });
    return response.data;
};

/**
 * Calcula los costos de una plantación forestal.
 * @param {Object} payload - Datos del cálculo
 */
export const calcularCostos = async (payload) => {
    const response = await api.post('/calcular-costos/', payload);
    return response.data;
};

export default api;
