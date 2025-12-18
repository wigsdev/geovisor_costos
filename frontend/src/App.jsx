/**
 * App.jsx - Componente principal del Geovisor de Costos Forestales
 */

import { useState, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import MapView from './components/MapView';
import { calcularCostos } from './services/api';
import './index.css';

function App() {
  // Estados de ubicación (elevados para compartir con MapView)
  const [selectedDepartamento, setSelectedDepartamento] = useState('');
  const [selectedProvincia, setSelectedProvincia] = useState('');
  const [selectedDistrito, setSelectedDistrito] = useState(null);
  const [selectedCultivo, setSelectedCultivo] = useState(null);

  // Estados de la aplicación
  const [polygonArea, setPolygonArea] = useState(null);
  const [hasPolygon, setHasPolygon] = useState(false);
  // Modal eliminado: ahora todo se controla desde el Sidebar
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handlePolygonCreated = useCallback((areaHa, layer) => {
    if (areaHa === null) {
      setPolygonArea(null);
      setHasPolygon(false);
      return;
    }
    setPolygonArea(areaHa);
    setHasPolygon(true);
    // Ya no abrimos modal, el usuario ve el sidebar actualizado
  }, []);

  // Calcular / Recalcular costos
  const handleCalculateWrapper = async (params) => {
    try {
      setIsLoading(true);
      const payload = {
        distrito_id: params.distritoId,
        cultivo_id: params.cultivoId,
        hectareas: params.hectareas,
        anio_inicio: params.anioInicio ?? 0,
        anio_fin: params.anioFin ?? 20,
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
      alert(`Error al calcular costos:\n${errorDetail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearResults = () => {
    setResults(null);
    // No limpiar el polígono para permitir recalcular con nuevos parámetros
    // setPolygonArea(null);
    // setHasPolygon(false);
  };

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
        onRecalculate={handleCalculateWrapper}
        hasPolygon={hasPolygon}
        hectareas={polygonArea}
        isLoading={isLoading}
      />

      <MapView
        onPolygonCreated={handlePolygonCreated}
        selectedDepartamento={selectedDepartamento}
        selectedProvincia={selectedProvincia}
        selectedDistrito={selectedDistrito}
        selectedCultivo={selectedCultivo}
      />
    </div>
  );
}

export default App;
