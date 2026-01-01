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
import { getDistritos, getCultivos, detectDistrito } from '../services/api';
// Librerías para parsing de archivos
import shp from 'shpjs';
import toGeoJSON from '@mapbox/togeojson';

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

    // Props de Modo (v1.3)
    inputMode,
    setInputMode,
    manualHectares,
    setManualHectares,

    hasPolygon,
    polygonArea, // Area del mapa (para visualizar)
    isLoading,
    onExternalPolygonLoaded, // Callback para App.jsx
    showToast // Nuevo prop
}) {
    const [allDistritos, setAllDistritos] = useState([]);
    const [cultivos, setCultivos] = useState([]);
    const [loading, setLoading] = useState(true);
    // Estado para Drag & Drop
    const [isDragging, setIsDragging] = useState(false);
    const [isParsing, setIsParsing] = useState(false);

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

    // Ref para evitar reset de selectores durante auto-detección
    const isAutoSelecting = useRef(false);

    // Cuando cambia el departamento, resetear provincia y distrito (sin auto-seleccionar)
    useEffect(() => {
        if (!isAutoSelecting.current) {
            setSelectedProvincia('');
            setSelectedDistrito(null);
        }
    }, [selectedDepartamento, setSelectedDistrito, setSelectedProvincia]);

    // Cuando cambia la provincia, resetear distrito (sin auto-seleccionar)
    useEffect(() => {
        if (!isAutoSelecting.current) {
            setSelectedDistrito(null);
        }
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

    // Efecto: Smart Default para Servicios según Hectáreas Activas
    // < 10 ha: Servicios desactivados (Pequeño productor)
    // >= 10 ha: Servicios activados (Mediano/Grande)
    useEffect(() => {
        const hec = inputMode === 'map' ? polygonArea : parseFloat(manualHectares);
        if (hec !== null && hec !== undefined && !isNaN(hec)) {
            setIncluirServicios(hec >= 10);
        }
    }, [polygonArea, manualHectares, inputMode]);

    // Manejar cambio de cultivo
    const handleCultivoChange = (e) => {
        const cultivo = cultivos.find(c => c.id === parseInt(e.target.value));
        setSelectedCultivo(cultivo || null);
    };

    // Wrapper para recalcular usando los nuevos inputs
    const handleRecalculateClick = () => {
        if (!selectedDistrito || !selectedCultivo) return;

        // Validar antes de enviar
        const hasMapArea = inputMode === 'map' && hasPolygon;
        const hasManualArea = inputMode === 'manual' && manualHectares && parseFloat(manualHectares) > 0;

        if (!hasMapArea && !hasManualArea) {
            return; // Disabled button should prevent this, but just in case
        }

        onRecalculate({
            distritoId: selectedDistrito.cod_ubigeo,
            cultivoId: selectedCultivo.id,
            hectareas: null, // App.jsx lo resolverá usando el state
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

    // Helper para determinar si el botón calcular está habilitado
    const canCalculate = useMemo(() => {
        if (!selectedDistrito || !selectedCultivo) return false;
        if (inputMode === 'map') return hasPolygon;
        if (inputMode === 'manual') return manualHectares && parseFloat(manualHectares) > 0;
        return false;
    }, [selectedDistrito, selectedCultivo, inputMode, hasPolygon, manualHectares]);

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

    // ==========================================
    // MANEJO DE ARCHIVOS (KML/SHP/GEOJSON)
    // ==========================================

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            await handleFileUpload(files[0]);
        }
    };



    const handleFileUpload = async (file) => {
        setIsParsing(true);
        try {
            let geojson = null;
            const fileName = file.name.toLowerCase();

            if (fileName.endsWith('.zip')) {
                // Shapefile (requiere ArrayBuffer)
                const buffer = await file.arrayBuffer();
                geojson = await shp(buffer);
            }
            else if (fileName.endsWith('.kml')) {
                // KML (XML String)
                const text = await file.text();
                const parser = new DOMParser();
                const kml = parser.parseFromString(text, 'text/xml');
                geojson = toGeoJSON.kml(kml);
            }
            else if (fileName.endsWith('.geojson') || fileName.endsWith('.json')) {
                // GeoJSON (JSON)
                const text = await file.text();
                geojson = JSON.parse(text);
            }
            else {
                showToast('Formato no soportado. Use .zip (Shapefile), .kml o .geojson', 'error');
                setIsParsing(false);
                return;
            }

            // Validar que sea un polígono válido
            if (!geojson || (!geojson.features && !geojson.geometry)) {
                throw new Error('No se encontraron geometrías válidas.');
            }

            // Normalizar a FeatureCollection si es Feature solo o Geometria sola
            // ... (simplificación: asumiendo FeatureCollection std o array de shp)
            if (Array.isArray(geojson)) geojson = geojson[0]; // shpjs a veces devuelve array

            // Extraer primera geometría (Polygon/MultiPolygon)
            const feature = geojson.features ? geojson.features.find(f =>
                f.geometry.type === 'Polygon' || f.geometry.type === 'MultiPolygon'
            ) : (geojson.type === 'Feature' ? geojson : null);

            if (!feature) {
                showToast('No se encontró ningún polígono en el archivo.', 'error');
                setIsParsing(false);
                return;
            }

            const finalGeoJSON = {
                type: 'FeatureCollection',
                features: [feature]
            };

            // Detectar Distrito (Smart Location)
            // Detectar Distrito (Smart Location)
            // Extraer el primer punto válido del polígono
            const getFirstCoordinate = (coords) => {
                if (!Array.isArray(coords)) return null;
                if (coords.length >= 2 && typeof coords[0] === 'number' && typeof coords[1] === 'number') {
                    return coords;
                }
                if (Array.isArray(coords[0])) {
                    return getFirstCoordinate(coords[0]);
                }
                return null;
            };

            const firstPoint = getFirstCoordinate(feature.geometry.coordinates);
            if (!firstPoint) {
                console.warn("No se pudieron extraer coordenadas del polígono");
                // Cargar sin detección
                onExternalPolygonLoaded(finalGeoJSON, null);
                setIsParsing(false);
                return;
            }

            const [lng, lat] = firstPoint;
            console.log('Detectando distrito para:', lat, lng);

            try {
                const detected = await detectDistrito(lat, lng);
                if (detected) {
                    const distObj = allDistritos.find(d => d.cod_ubigeo === detected.cod_ubigeo);
                    if (distObj) {
                        console.log(`Distrito detectado: ${distObj.nombre}, ${distObj.provincia}`);

                        // Notificar a App.jsx CON el distrito detectado
                        onExternalPolygonLoaded(finalGeoJSON, distObj.cod_ubigeo);

                        // Activar bandera para bloquear resets automáticos
                        isAutoSelecting.current = true;

                        // Actualizar UI en cascada
                        // Al usar useMemo, las listas de provincias/distritos se calculan al vuelo 
                        // basándose en los nuevos valores, así que podemos setear todo junto.
                        setSelectedDepartamento(distObj.departamento);
                        setSelectedProvincia(distObj.provincia);
                        setSelectedDistrito(distObj);

                        showToast(`Ubicación detectada: ${distObj.nombre}, ${distObj.provincia}`, 'success');

                        // Liberar bandera después de un ciclo de render
                        setTimeout(() => {
                            isAutoSelecting.current = false;
                        }, 500);

                    } else {
                        console.warn("Distrito detectado pero no encontrado localmente.");
                        onExternalPolygonLoaded(finalGeoJSON, null);
                    }
                } else {
                    onExternalPolygonLoaded(finalGeoJSON, null);
                }
            } catch (err) {
                console.warn('Auto-detección falló', err);
                onExternalPolygonLoaded(finalGeoJSON, null);
            }
        } catch (error) {
            console.error(error);
            showToast('Error al leer el archivo: ' + error.message, 'error');
        } finally {
            setIsParsing(false);
        }
    };
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
                        onRecalculate={handleRecalculateClick}
                        distrito={selectedDistrito}
                        cultivo={selectedCultivo}
                        hectareas={inputMode === 'map' ? polygonArea : parseFloat(manualHectares)}
                    />
                ) : (
                    <>
                        {/* 1. MODO DE ENTRADA (Tabs) */}
                        <div className="toggle-container mb-6">
                            <button
                                onClick={() => setInputMode('map')}
                                className={`toggle-btn ${inputMode === 'map' ? 'active' : ''}`}
                            >
                                <span className="mr-2">📍</span> Mapa
                            </button>
                            <button
                                onClick={() => setInputMode('manual')}
                                className={`toggle-btn ${inputMode === 'manual' ? 'active' : ''}`}
                            >
                                <span className="mr-2">📝</span> Manual
                            </button>
                        </div>

                        {/* Hidden Input for File Upload (Moved outside dropzone to prevent double-click) */}
                        <input
                            type="file"
                            id="file-upload"
                            className="hidden"
                            accept=".kml,.zip,.json,.geojson"
                            onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                        />

                        {/* AREA INPUT / DROPZONE */}
                        {inputMode === 'map' ? (
                            hasPolygon ? (
                                <div className="bg-emerald-900/30 p-4 rounded border border-emerald-500/50 mb-6 animate-pulse-slow">
                                    <div className="flex justify-between items-center mb-1">
                                        <span className="text-emerald-400 font-medium">Área Definida</span>
                                        <span className="bg-emerald-500 text-white text-xs px-2 py-0.5 rounded-full">OK</span>
                                    </div>
                                    <div className="text-2xl font-bold text-white tracking-wide">
                                        {polygonArea} <span className="text-sm font-normal text-emerald-300">ha</span>
                                    </div>
                                    <div className="text-xs text-emerald-400 mt-1 opacity-80">
                                        Polígono activo en mapa
                                    </div>
                                </div>
                            ) : (
                                <div
                                    className={`p-6 rounded border-2 border-dashed mb-6 transition-all text-center cursor-pointer
                                ${isDragging
                                            ? 'border-emerald-400 bg-emerald-900/20 scale-105'
                                            : 'border-slate-700 bg-slate-800/50 hover:border-slate-500'
                                        }
                            `}
                                    onDragOver={handleDragOver}
                                    onDragLeave={handleDragLeave}
                                    onDrop={handleDrop}
                                    onClick={() => document.getElementById('file-upload').click()}
                                >
                                    {isParsing ? (
                                        <div className="text-emerald-400 animate-pulse">
                                            <span className="block text-2xl mb-2">⚙️</span>
                                            Procesando archivo...
                                        </div>
                                    ) : (
                                        <>
                                            <div className="text-4xl mb-3 opacity-50">📂</div>
                                            <h3 className="text-slate-200 font-bold mb-1">Dibuja o Arrastra</h3>
                                            <p className="text-xs text-slate-400 leading-relaxed">
                                                Use las herramientas de dibujo <br />
                                                o suba un archivo (KML, Zip/Shp)
                                            </p>
                                        </>
                                    )}
                                </div>
                            )
                        ) : (
                            /* MODO MANUAL */
                            <div className="bg-slate-800 p-4 rounded border border-slate-700">
                                <label className="form-label text-emerald-400">Ingrese Hectáreas</label>
                                <div className="relative">
                                    <input
                                        type="number"
                                        min="0.1"
                                        step="0.1"
                                        placeholder="Ej: 10.5"
                                        value={manualHectares}
                                        onChange={(e) => setManualHectares(e.target.value)}
                                        className="form-input w-full bg-slate-900 text-white rounded p-3 text-lg font-bold border border-slate-600 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                                        autoFocus
                                    />
                                    <div className="absolute right-3 top-3.5 text-slate-500 font-bold text-sm pointer-events-none">
                                        HA
                                    </div>
                                </div>
                                <p className="text-xs text-slate-500 mt-2">
                                    Ingrese el tamaño total del área a reforestar.
                                </p>
                            </div>
                        )}

                        {/* 3. UBICACIÓN (Contexto) */}
                        <div className="mb-6 border-t border-slate-700 pt-6">
                            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wide mb-3">
                                📍 Ubicación del Predio
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

                        {/* 4. CULTIVO */}
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
                                            disabled={!canCalculate || isLoading}
                                            className={`w-full py-3 px-4 rounded font-bold shadow-lg transition-all ${canCalculate
                                                ? 'bg-emerald-600 hover:bg-emerald-500 text-white transform hover:scale-[1.02]'
                                                : 'bg-slate-700 text-slate-400 cursor-not-allowed'
                                                }`}
                                        >
                                            {isLoading ? '⏳ Calculando...' : '🧮 Calcular Costos'}
                                        </button>

                                        {/* Mensajes de Validación */}
                                        {!canCalculate && inputMode === 'map' && !hasPolygon && (
                                            <p className="text-xs text-center text-amber-500 mt-2">
                                                ⚠️ Dibuja un polígono para continuar
                                            </p>
                                        )}
                                        {!canCalculate && inputMode === 'manual' && (!manualHectares || manualHectares <= 0) && (
                                            <p className="text-xs text-center text-amber-500 mt-2">
                                                ⚠️ Ingrese un valor de hectáreas válido
                                            </p>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

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
                v1.3 - Geovisor Costos Forestales
            </div>
        </div >
    );
}
