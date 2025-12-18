/**
 * Servicio API para el Geovisor de Costos Forestales.
 * Gestiona las llamadas al backend Django.
 */

import axios from 'axios';

// Base URL del backend Django
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

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
 */
export const getCultivos = async () => {
    const response = await api.get('/cultivos/');
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
