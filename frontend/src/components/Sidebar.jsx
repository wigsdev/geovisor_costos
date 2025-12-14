/**
 * Sidebar - Panel Lateral del Geovisor
 * 
 * Contiene:
 * - Selectores en cascada: Departamento → Provincia → Distrito
 * - Selector de Cultivo
 * - Instrucciones para dibujar
 * - Panel de Resultados
 */

import { useState, useEffect, useMemo, useRef } from 'react';
import ResultsPanel from './ResultsPanel';
import { getDistritos, getCultivos } from '../services/api';

// Datos de respaldo si la API no responde
const DISTRITOS_FALLBACK = [
    { cod_ubigeo: '221005', nombre: 'UCHIZA', departamento: 'SAN MARTIN', provincia: 'TOCACHE', costo_jornal_sugerido: '50.00', costo_planton_sugerido: '0.80' },
];

const CULTIVOS_FALLBACK = [
    { id: 1, nombre: 'Bolaina Blanca', turno_estimado: 8, densidad_base: 1111 },
];

export default function Sidebar({
    selectedDistrito,
    setSelectedDistrito,
    selectedCultivo,
    setSelectedCultivo,
    results,
    onClearResults,
    onRecalculate,
    hasPolygon,
    hectareas
}) {
    const [allDistritos, setAllDistritos] = useState([]);
    const [cultivos, setCultivos] = useState([]);
    const [loading, setLoading] = useState(true);

    // Estados para los selectores en cascada
    const [selectedDepartamento, setSelectedDepartamento] = useState('');
    const [selectedProvincia, setSelectedProvincia] = useState('');

    // Refs para auto-focus en selectores
    const provinciaRef = useRef(null);
    const distritoRef = useRef(null);

    // Cargar datos al montar
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [distritosData, cultivosData] = await Promise.all([
                    getDistritos(),
                    getCultivos()
                ]);
                const distritosToUse = distritosData.length > 0 ? distritosData : DISTRITOS_FALLBACK;
                setAllDistritos(distritosToUse);
                setCultivos(cultivosData.length > 0 ? cultivosData : CULTIVOS_FALLBACK);

                // Seleccionar primer departamento por defecto
                const departamentos = [...new Set(distritosToUse.map(d => d.departamento))].sort();
                if (departamentos.length > 0) {
                    setSelectedDepartamento(departamentos[0]);
                }

                // Seleccionar primer cultivo
                if (cultivosData.length > 0) setSelectedCultivo(cultivosData[0]);
            } catch (error) {
                console.warn('Error cargando datos, usando fallback:', error);
                setAllDistritos(DISTRITOS_FALLBACK);
                setCultivos(CULTIVOS_FALLBACK);
                setSelectedDepartamento(DISTRITOS_FALLBACK[0].departamento);
                setSelectedCultivo(CULTIVOS_FALLBACK[0]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [setSelectedCultivo]);

    // Lista única de departamentos
    const departamentos = useMemo(() => {
        return [...new Set(allDistritos.map(d => d.departamento))].filter(Boolean).sort();
    }, [allDistritos]);

    // Lista de provincias filtrada por departamento seleccionado
    const provincias = useMemo(() => {
        if (!selectedDepartamento) return [];
        return [...new Set(
            allDistritos
                .filter(d => d.departamento === selectedDepartamento)
                .map(d => d.provincia)
        )].filter(Boolean).sort();
    }, [allDistritos, selectedDepartamento]);

    // Lista de distritos filtrada por provincia seleccionada
    const distritos = useMemo(() => {
        if (!selectedProvincia) return [];
        return allDistritos
            .filter(d => d.departamento === selectedDepartamento && d.provincia === selectedProvincia)
            .sort((a, b) => a.nombre.localeCompare(b.nombre));
    }, [allDistritos, selectedDepartamento, selectedProvincia]);

    // Cuando cambia el departamento, resetear provincia y distrito
    useEffect(() => {
        if (provincias.length > 0) {
            setSelectedProvincia(provincias[0]);
        } else {
            setSelectedProvincia('');
            setSelectedDistrito(null);
        }
    }, [selectedDepartamento, provincias, setSelectedDistrito]);

    // Cuando cambia la provincia, seleccionar primer distrito
    useEffect(() => {
        if (distritos.length > 0) {
            setSelectedDistrito(distritos[0]);
        } else {
            setSelectedDistrito(null);
        }
    }, [selectedProvincia, distritos, setSelectedDistrito]);

    // Manejar cambio de departamento - auto-focus a provincia
    const handleDepartamentoChange = (e) => {
        setSelectedDepartamento(e.target.value);
        // Hacer focus al selector de provincia después de un breve delay
        setTimeout(() => {
            provinciaRef.current?.focus();
        }, 100);
    };

    // Manejar cambio de provincia - auto-focus a distrito
    const handleProvinciaChange = (e) => {
        setSelectedProvincia(e.target.value);
        // Hacer focus al selector de distrito después de un breve delay
        setTimeout(() => {
            distritoRef.current?.focus();
        }, 100);
    };

    // Manejar cambio de distrito
    const handleDistritoChange = (e) => {
        const distrito = distritos.find(d => d.cod_ubigeo === e.target.value);
        setSelectedDistrito(distrito || null);
    };

    // Manejar cambio de cultivo
    const handleCultivoChange = (e) => {
        const cultivo = cultivos.find(c => c.id === parseInt(e.target.value));
        setSelectedCultivo(cultivo || null);
    };

    if (loading) {
        return (
            <div className="sidebar">
                <div className="p-4 text-center">
                    <div className="animate-spin inline-block w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full"></div>
                    <p className="mt-2 text-slate-400">Cargando datos...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="sidebar">
            {/* Header */}
            <div className="sidebar-header">
                <h1 className="text-xl font-bold text-white">🌲 Geovisor</h1>
                <p className="text-sm text-slate-400">Costos de Plantaciones Forestales</p>
            </div>

            {/* Content */}
            <div className="sidebar-content">
                {results ? (
                    <ResultsPanel
                        results={results}
                        onClear={onClearResults}
                        onRecalculate={onRecalculate}
                        distrito={selectedDistrito}
                        cultivo={selectedCultivo}
                        hectareas={hectareas}
                    />
                ) : (
                    <>
                        {/* Sección de Contexto */}
                        <div className="mb-6">
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
                                📍 Ubicación
                            </h3>

                            {/* Selector de Departamento */}
                            <div className="form-group">
                                <label className="form-label">Departamento</label>
                                <select
                                    value={selectedDepartamento}
                                    onChange={handleDepartamentoChange}
                                    className="form-select"
                                >
                                    {departamentos.map(d => (
                                        <option key={d} value={d}>{d}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Selector de Provincia */}
                            <div className="form-group">
                                <label className="form-label">Provincia</label>
                                <select
                                    ref={provinciaRef}
                                    value={selectedProvincia}
                                    onChange={handleProvinciaChange}
                                    className="form-select"
                                    disabled={provincias.length === 0}
                                >
                                    {provincias.map(p => (
                                        <option key={p} value={p}>{p}</option>
                                    ))}
                                </select>
                            </div>

                            {/* Selector de Distrito */}
                            <div className="form-group">
                                <label className="form-label">Distrito</label>
                                <select
                                    ref={distritoRef}
                                    value={selectedDistrito?.cod_ubigeo || ''}
                                    onChange={handleDistritoChange}
                                    className="form-select"
                                    disabled={distritos.length === 0}
                                >
                                    {distritos.map(d => (
                                        <option key={d.cod_ubigeo} value={d.cod_ubigeo}>
                                            {d.nombre}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {/* Sección de Cultivo */}
                        <div className="mb-6">
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
                                🌱 Especie
                            </h3>
                            <div className="form-group">
                                <label className="form-label">Cultivo Forestal</label>
                                <select
                                    value={selectedCultivo?.id || ''}
                                    onChange={handleCultivoChange}
                                    className="form-select"
                                >
                                    {cultivos.map(c => (
                                        <option key={c.id} value={c.id}>
                                            {c.nombre}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        {/* Instrucciones */}
                        <div className="mb-6">
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
                                📐 Área de Plantación
                            </h3>
                            <div className="instruction-box">
                                {hasPolygon ? (
                                    <p className="text-emerald-400">
                                        ✅ Área dibujada. Ajuste los datos en el modal.
                                    </p>
                                ) : (
                                    <p className="text-slate-300">
                                        Use la herramienta <strong>polígono</strong> 🔷 en el mapa para dibujar su área de plantación.
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Info del distrito */}
                        {selectedDistrito && (
                            <div className="info-card">
                                <h4 className="font-semibold text-white mb-2">
                                    {selectedDistrito.nombre}
                                </h4>
                                <div className="text-sm text-slate-400 space-y-1">
                                    <p>Ubigeo: {selectedDistrito.cod_ubigeo}</p>
                                    <p>Jornal sugerido: S/ {selectedDistrito.costo_jornal_sugerido}</p>
                                    <p>Plantón sugerido: S/ {selectedDistrito.costo_planton_sugerido}</p>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Footer */}
            <div className="sidebar-footer">
                <p className="text-xs text-slate-500">
                    v2.0 - Geovisor Costos Forestales
                </p>
            </div>
        </div>
    );
}
