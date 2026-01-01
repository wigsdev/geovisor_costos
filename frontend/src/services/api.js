import axios from 'axios';

// Base URL del backend Django
// 1. Usa VITE_API_URL si está definido en Railway.
// 2. Si no, intenta usar el backend predecible (geovisor-costos-backend.up.railway.app).
// 3. En desarrollo local, usa '/api' que el proxy de Vite redirige a localhost:8000.

const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '/api' : 'https://geovisorcostos-production.up.railway.app/api');

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

export const calcularCostos = async (payload) => {
    const response = await api.post('/calcular-costos/', payload);
    return response.data;
};

/**
 * Detecta el distrito más cercano a una coordenada.
 * @param {number} lat - Latitud
 * @param {number} lng - Longitud
 */
export const detectDistrito = async (lat, lng) => {
    const response = await api.get('/distritos/detectar/', {
        params: { lat, lng }
    });
    return response.data;
};

export default api;
