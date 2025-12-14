/**
 * App.jsx - Componente principal del Geovisor de Costos Forestales
 */

import { useState, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import MapView from './components/MapView';
import PlantingConfigModal from './components/PlantingConfigModal';
import { calcularCostos } from './services/api';
import './index.css';

function App() {
  const [selectedDistrito, setSelectedDistrito] = useState(null);
  const [selectedCultivo, setSelectedCultivo] = useState(null);
  const [polygonArea, setPolygonArea] = useState(null);
  const [hasPolygon, setHasPolygon] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
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
    setIsModalOpen(true);
  }, []);

  const handleCalculate = async (payload) => {
    setIsLoading(true);
    try {
      const data = await calcularCostos(payload);
      setResults(data);
      setIsModalOpen(false);
    } catch (err) {
      console.error('Error:', err);
      const errorDetail = err.response?.data
        ? JSON.stringify(err.response.data, null, 2)
        : 'No se pudo conectar con el servidor';
      alert(`Error del servidor:\n${errorDetail}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearResults = () => {
    setResults(null);
    setPolygonArea(null);
    setHasPolygon(false);
  };

  const handleRecalculate = () => {
    setResults(null);
    setIsModalOpen(true);
  };

  return (
    <div className="app-container">
      <Sidebar
        selectedDistrito={selectedDistrito}
        setSelectedDistrito={setSelectedDistrito}
        selectedCultivo={selectedCultivo}
        setSelectedCultivo={setSelectedCultivo}
        results={results}
        onClearResults={handleClearResults}
        onRecalculate={handleRecalculate}
        hasPolygon={hasPolygon}
      />

      <MapView onPolygonCreated={handlePolygonCreated} />

      <PlantingConfigModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCalculate}
        hectareas={polygonArea}
        distrito={selectedDistrito}
        cultivo={selectedCultivo}
        isLoading={isLoading}
      />
    </div>
  );
}

export default App;
