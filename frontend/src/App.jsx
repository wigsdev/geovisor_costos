/**
 * App.jsx - Componente principal del Geovisor de Costos Forestales
 */

import { useState, useCallback, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MapView from './components/MapView';
import Notification from './components/Notification';
import { calcularCostos } from './services/api';
import './index.css';

function App() {
  // Estados de ubicación (elevados para compartir con MapView)
  const [selectedDepartamento, setSelectedDepartamento] = useState('');
  const [selectedProvincia, setSelectedProvincia] = useState('');
  const [selectedDistrito, setSelectedDistrito] = useState(null);
  const [selectedCultivo, setSelectedCultivo] = useState(null);

  // Estados de la aplicación
  const [inputMode, setInputMode] = useState('map'); // 'map' | 'manual'
  const [manualHectares, setManualHectares] = useState(''); // Input manual
  const [uploadedGeoJSON, setUploadedGeoJSON] = useState(null); // Nuevo estado para archivos cargados
  const [polygonArea, setPolygonArea] = useState(null);
  const [hasPolygon, setHasPolygon] = useState(false);

  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Toast State
  const [toast, setToast] = useState({ message: '', type: 'info', visible: false });

  const showToast = useCallback((message, type = 'info') => {
    setToast({ message, type, visible: true });
  }, []);

  const closeToast = useCallback(() => {
    setToast(prev => ({ ...prev, visible: false }));
  }, []);

  // resetear results si cambia modo
  useEffect(() => {
    setResults(null);
  }, [inputMode]);

  // Callback para archivos cargados
  const handleExternalPolygon = useCallback((geoJSON, distritoUbigeo) => {
    setUploadedGeoJSON(geoJSON);
    setInputMode('map');
    // Si viene distrito, ya fue notificado por sidebar
  }, []);

  // Modal eliminado: ahora todo se controla desde el Sidebar

  const handlePolygonCreated = useCallback((areaHa, layer) => {
    if (areaHa === null) {
      // User requested delete: Reset everything
      handleResetAll();
      return;
    }
    setPolygonArea(areaHa);
    setHasPolygon(true);
    // Auto-switch a modo mapa si dibuja
    if (inputMode !== 'map') setInputMode('map');
  }, [inputMode]);

  // Calcular / Recalcular costos
  const handleCalculateWrapper = async (params) => {
    try {
      setIsLoading(true);

      // Determinar fuente de hectáreas
      const hectareasFinal = inputMode === 'map' ? polygonArea : parseFloat(manualHectares);

      // Validación simple
      if (!hectareasFinal || hectareasFinal <= 0) {
        showToast('Por favor ingrese un número de hectáreas válido o dibuje un polígono.', 'error');
        setIsLoading(false);
        return;
      }

      const payload = {
        distrito_id: params.distritoId,
        cultivo_id: params.cultivoId,
        hectareas: hectareasFinal,
        anio_inicio: params.anioInicio ?? 0,
        anio_fin: params.anioFin ?? 20,
        incluir_servicios: params.incluirServicios ?? true,
        // Parámetros v1.1
        sistema_siembra: params.sistemaSiembra,
        distanciamiento_largo: params.distanciaLargo,
        distanciamiento_ancho: params.distanciaAncho,
        costo_jornal_usuario: params.costoJornal,
        costo_planton_usuario: params.costoPlanton
      };

      const data = await calcularCostos(payload);
      setResults(data);
    } catch (error) {
      console.error('Error calculando costos:', error);
      const errorDetail = error.response?.data
        ? JSON.stringify(error.response.data, null, 2)
        : 'Error de conexión';
      showToast('Error al calcular costos. Revise la consola.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearResults = useCallback(() => {
    setResults(null);
    // Solo limpia resultados, mantiene inputs y polígono (Modo Editar)
  }, []);

  const handleResetAll = useCallback(() => {
    setResults(null);
    setPolygonArea(null);
    setHasPolygon(false);
    setInputMode('map');
    setManualHectares('');
    setSelectedDistrito(null);
    setSelectedCultivo(null);
    setSelectedDepartamento(''); // Reset explicit
    setSelectedProvincia(''); // Reset explicit
    setUploadedGeoJSON(null);
    showToast('Formulario reiniciado', 'info');
  }, [showToast]);

  return (
    <div className="app-container">
      <Sidebar
        selectedDepartamento={selectedDepartamento}
        setSelectedDepartamento={setSelectedDepartamento}
        selectedProvincia={selectedProvincia}
        setSelectedProvincia={setSelectedProvincia}
        selectedDistrito={selectedDistrito}
        setSelectedDistrito={setSelectedDistrito}
        selectedCultivo={selectedCultivo}
        setSelectedCultivo={setSelectedCultivo}
        results={results}
        onClearResults={handleClearResults}
        onResetAll={handleResetAll}
        onRecalculate={handleCalculateWrapper}
        inputMode={inputMode}
        setInputMode={setInputMode}
        manualHectares={manualHectares}
        setManualHectares={setManualHectares}
        hasPolygon={hasPolygon}
        polygonArea={polygonArea}
        isLoading={isLoading}
        onExternalPolygonLoaded={handleExternalPolygon}
        showToast={showToast}
      />
      <MapView
        onPolygonCreated={handlePolygonCreated}
        selectedDepartamento={selectedDepartamento}
        selectedProvincia={selectedProvincia}
        selectedDistrito={selectedDistrito}
        selectedCultivo={selectedCultivo}
        canDraw={inputMode === 'map'}
        uploadedGeoJSON={uploadedGeoJSON}
      />

      {toast.visible && (
        <Notification
          message={toast.message}
          type={toast.type}
          onClose={closeToast}
        />
      )}
    </div>
  );
}

export default App;
