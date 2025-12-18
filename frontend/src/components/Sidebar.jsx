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
    selectedDepartamento,
    setSelectedDepartamento,
    selectedProvincia,
    setSelectedProvincia,
    selectedDistrito,
    setSelectedDistrito,
    selectedCultivo,
    setSelectedCultivo,
    results,
    onClearResults,
    onResetAll,
    onRecalculate,
    hasPolygon,
    hectareas,
    isLoading
}) {
    const [allDistritos, setAllDistritos] = useState([]);
    const [cultivos, setCultivos] = useState([]);
    const [loading, setLoading] = useState(true);

    // State para inputs de configuración de siembra
    const [sistemaSiembra, setSistemaSiembra] = useState('CUADRADO');
    const [distanciaLargo, setDistanciaLargo] = useState('3.00');
    const [distanciaAncho, setDistanciaAncho] = useState('3.00');

    // State para Smart Defaults (Costos)
    const [costoJornal, setCostoJornal] = useState('50.00');
    const [costoPlanton, setCostoPlanton] = useState('1.00');

    // State para Rango de Años
    const [anioInicio, setAnioInicio] = useState(0);
    const [anioFin, setAnioFin] = useState(20);
    const [incluirServicios, setIncluirServicios] = useState(true);

    // Refs para auto-focus en selectores
    const provinciaRef = useRef(null);
    const distritoRef = useRef(null);
    const cultivoRef = useRef(null);

    // Cargar distritos al montar
    useEffect(() => {
        const fetchData = async () => {
            try {
                const distritosData = await getDistritos();
                const distritosToUse = distritosData.length > 0 ? distritosData : DISTRITOS_FALLBACK;
                setAllDistritos(distritosToUse);
            } catch (error) {
                console.warn('Error cargando distritos, usando fallback:', error);
                setAllDistritos(DISTRITOS_FALLBACK);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Cargar/Filtrar Cultivos cuando cambia el Distrito
    useEffect(() => {
        const fetchCultivos = async () => {
            if (!selectedDistrito) {
                setCultivos([]);
                return;
            }

            try {
                // Aplicar Filtro Regional: Traer solo cultivos válidos para este distrito
                const cultivosData = await getCultivos(selectedDistrito.cod_ubigeo);
                setCultivos(cultivosData.length > 0 ? cultivosData : CULTIVOS_FALLBACK);

                // Aplicar Smart Defaults de Precio
                if (selectedDistrito.costo_jornal_sugerido) {
                    setCostoJornal(selectedDistrito.costo_jornal_sugerido);
                }
                if (selectedDistrito.costo_planton_sugerido) {
                    setCostoPlanton(selectedDistrito.costo_planton_sugerido);
                }
            } catch (error) {
                console.warn('Error cargando cultivos:', error);
                setCultivos(CULTIVOS_FALLBACK);
            }
        };

        fetchCultivos();
    }, [selectedDistrito]);


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

    // Cuando cambia el departamento, resetear provincia y distrito (sin auto-seleccionar)
    useEffect(() => {
        setSelectedProvincia('');
        setSelectedDistrito(null);
    }, [selectedDepartamento, setSelectedDistrito]);

    // Cuando cambia la provincia, resetear distrito (sin auto-seleccionar)
    useEffect(() => {
        setSelectedDistrito(null);
    }, [selectedProvincia, setSelectedDistrito]);

    // Manejar cambio de departamento - auto-focus a provincia
    const handleDepartamentoChange = (e) => {
        setSelectedDepartamento(e.target.value);
        setTimeout(() => provinciaRef.current?.focus(), 100);
    };

    // Manejar cambio de provincia - auto-focus a distrito
    const handleProvinciaChange = (e) => {
        setSelectedProvincia(e.target.value);
        setTimeout(() => distritoRef.current?.focus(), 100);
    };

    // Manejar cambio de distrito
    const handleDistritoChange = (e) => {
        const distrito = distritos.find(d => d.cod_ubigeo === e.target.value);
        setSelectedDistrito(distrito || null);
        setTimeout(() => cultivoRef.current?.focus(), 100);
    };



    // Efecto: Smart Default para Servicios según Hectáreas
    // < 10 ha: Servicios desactivados (Pequeño productor)
    // >= 10 ha: Servicios activados (Mediano/Grande)
    useEffect(() => {
        if (hectareas !== null && hectareas !== undefined) {
            setIncluirServicios(hectareas >= 10);
        }
    }, [hectareas]);

    // Manejar cambio de cultivo
    const handleCultivoChange = (e) => {
        const cultivo = cultivos.find(c => c.id === parseInt(e.target.value));
        setSelectedCultivo(cultivo || null);
    };

    // Wrapper para recalcular usando los nuevos inputs
    const handleRecalculateClick = () => {
        if (!selectedDistrito || !selectedCultivo) return;

        onRecalculate({
            distritoId: selectedDistrito.cod_ubigeo,
            cultivoId: selectedCultivo.id,
            hectareas: hectareas,
            sistemaSiembra,
            distanciaLargo,
            distanciaAncho: sistemaSiembra === 'RECTANGULAR' ? distanciaAncho : null,
            costoJornal,
            costoPlanton,
            anioInicio,
            anioFin,
            incluirServicios
        });
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
                        onReset={onResetAll}
                        onRecalculate={handleRecalculateClick} // Pasamos la nueva funcion wrapper
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
                                    <option value="">-- Seleccione departamento --</option>
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
                                    disabled={!selectedDepartamento}
                                >
                                    <option value="">-- Seleccione provincia --</option>
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
                                    disabled={!selectedProvincia}
                                >
                                    <option value="">-- Seleccione distrito --</option>
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
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3 border-t border-slate-700 pt-4">
                                🌱 Configuración de Cultivo
                            </h3>

                            {/* Selector de Especie - Ahora dependiente de la zona */}
                            <div className="form-group">
                                <label className="form-label">Especie Forestal</label>
                                <select
                                    ref={cultivoRef}
                                    value={selectedCultivo?.id || ''}
                                    onChange={handleCultivoChange}
                                    className="form-select"
                                    disabled={!selectedDistrito}
                                >
                                    <option value="">-- Seleccione especie --</option>
                                    {cultivos.map(c => (
                                        <option key={c.id} value={c.id}>
                                            {c.nombre}
                                        </option>
                                    ))}
                                </select>
                                {!selectedDistrito && <p className="text-xs text-slate-500 mt-1">Seleccione un distrito primero</p>}
                            </div>

                            {/* Inputs de Geometría (Solo si hay especie seleccionada) */}
                            {selectedCultivo && (
                                <div className="animate-fade-in space-y-4">
                                    <div className="form-group">
                                        <label className="form-label">Sistema de Siembra</label>
                                        <select
                                            value={sistemaSiembra}
                                            onChange={(e) => setSistemaSiembra(e.target.value)}
                                            className="form-select"
                                        >
                                            <option value="CUADRADO">Cuadrado</option>
                                            <option value="RECTANGULAR">Rectangular</option>
                                            <option value="TRES_BOLILLO">Tres Bolillo</option>
                                        </select>
                                    </div>

                                    <div className="grid grid-cols-2 gap-2">
                                        <div className="form-group">
                                            <label className="form-label text-xs">Distancia Filas (m)</label>
                                            <input
                                                type="number"
                                                step="0.1"
                                                value={distanciaLargo}
                                                onChange={(e) => setDistanciaLargo(e.target.value)}
                                                className="form-input w-full bg-slate-800 text-white rounded p-2 text-sm border border-slate-600"
                                            />
                                        </div>
                                        {sistemaSiembra === 'RECTANGULAR' && (
                                            <div className="form-group">
                                                <label className="form-label text-xs">Distancia Plantas (m)</label>
                                                <input
                                                    type="number"
                                                    step="0.1"
                                                    value={distanciaAncho}
                                                    onChange={(e) => setDistanciaAncho(e.target.value)}
                                                    className="form-input w-full bg-slate-800 text-white rounded p-2 text-sm border border-slate-600"
                                                />
                                            </div>
                                        )}
                                    </div>

                                    {/* Costos Editables (Smart Defaults) */}
                                    <div className="grid grid-cols-2 gap-2 border-t border-slate-700 pt-3 mt-3">
                                        <div className="form-group">
                                            <label className="form-label text-xs text-emerald-400">Jornal (S/)</label>
                                            <input
                                                type="number"
                                                step="1"
                                                value={costoJornal}
                                                onChange={(e) => setCostoJornal(e.target.value)}
                                                className="form-input w-full bg-slate-800 text-white rounded p-2 text-sm border border-slate-600"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label className="form-label text-xs text-emerald-400">Plantón (S/)</label>
                                            <input
                                                type="number"
                                                step="0.10"
                                                value={costoPlanton}
                                                onChange={(e) => setCostoPlanton(e.target.value)}
                                                className="form-input w-full bg-slate-800 text-white rounded p-2 text-sm border border-slate-600"
                                            />
                                        </div>
                                    </div>

                                    {/* Rango de Años */}
                                    <div className="grid grid-cols-2 gap-2 mt-2">
                                        <div className="form-group">
                                            <label className="form-label text-xs">Año Inicio</label>
                                            <input
                                                type="number"
                                                min="0"
                                                max="20"
                                                value={anioInicio}
                                                onChange={(e) => setAnioInicio(parseInt(e.target.value) || 0)}
                                                className="form-input w-full bg-slate-800 text-white rounded p-2 text-sm border border-slate-600"
                                            />
                                        </div>
                                        <div className="form-group">
                                            <label className="form-label text-xs">Año Fin</label>
                                            <input
                                                type="number"
                                                min="0"
                                                max="20"
                                                value={anioFin}
                                                onChange={(e) => setAnioFin(parseInt(e.target.value) || 0)}
                                                className="form-input w-full bg-slate-800 text-white rounded p-2 text-sm border border-slate-600"
                                            />
                                        </div>
                                    </div>

                                    {/* Servicios Opcionales */}
                                    <div className="mt-3 pt-3 border-t border-slate-700">
                                        <label className="flex items-center space-x-2 cursor-pointer">
                                            <input
                                                type="checkbox"
                                                checked={incluirServicios}
                                                onChange={(e) => setIncluirServicios(e.target.checked)}
                                                className="form-checkbox text-emerald-500 rounded bg-slate-700 border-slate-500 focus:ring-emerald-500"
                                            />
                                            <span className="text-sm text-slate-300">Incluir Servicios (Gestión/Técnica)</span>
                                        </label>
                                    </div>

                                    {/* Botón Calcular Principal */}
                                    <div className="pt-4 mt-2">
                                        <button
                                            onClick={handleRecalculateClick}
                                            disabled={!hasPolygon || isLoading}
                                            className={`w-full py-3 px-4 rounded font-bold shadow-lg transition-all ${hasPolygon
                                                ? 'bg-emerald-600 hover:bg-emerald-500 text-white transform hover:scale-[1.02]'
                                                : 'bg-slate-700 text-slate-400 cursor-not-allowed'
                                                }`}
                                        >
                                            {isLoading ? '⏳ Calculando...' : '🧮 Calcular Costos'}
                                        </button>
                                        {!hasPolygon && (
                                            <p className="text-xs text-center text-amber-500 mt-2">
                                                ⚠️ Dibuja un polígono en el mapa para activar
                                            </p>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Instrucciones (Solo si no hay polígono) */}
                        {!hasPolygon && (
                            <div className="mb-6 animate-fade-in">
                                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
                                    📐 Área de Plantación
                                </h3>
                                <div className="instruction-box">
                                    <p className="text-slate-300">
                                        Use la herramienta <strong>polígono</strong> 🔷 en el mapa para dibujar su área de plantación.
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Info del distrito */}
                        {selectedDistrito && (
                            <div className="info-card">
                                <h4 className="font-semibold text-white mb-2">
                                    {selectedDistrito.nombre}
                                </h4>
                                <div className="text-sm text-slate-400 space-y-1">
                                    <p>Ubigeo: {selectedDistrito.cod_ubigeo}</p>
                                    <p className="text-xs text-slate-500 italic">Precios sugeridos cargados automáticamente.</p>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>

            <div className="absolute bottom-0 w-80 bg-gray-900 border-t border-gray-700 p-2 text-center text-xs text-gray-500">
                v1.1 - Geovisor Costos Forestales
            </div>
        </div >
    );
}
