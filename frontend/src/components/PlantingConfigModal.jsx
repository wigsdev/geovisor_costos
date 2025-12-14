/**
 * PlantingConfigModal - Modal de Configuración de Siembra
 * 
 * Aparece después de draw:created para configurar:
 * - Sistema de siembra (Cuadrado, Rectangular, Tres Bolillo)
 * - Distancias de plantación
 * - Costos editables (Smart Defaults)
 * - Rango de años
 */

import { useState, useEffect } from 'react';

// Opciones de sistemas de siembra
const SISTEMAS_SIEMBRA = [
    { value: 'CUADRADO', label: 'Cuadrado (distancia × distancia)' },
    { value: 'RECTANGULAR', label: 'Rectangular (largo × ancho)' },
    { value: 'TRES_BOLILLO', label: 'Tres Bolillo (triángulo equilátero)' },
];

export default function PlantingConfigModal({
    isOpen,
    onClose,
    onSubmit,
    hectareas,
    distrito,
    cultivo,
    isLoading
}) {
    // Estado del formulario
    const [formData, setFormData] = useState({
        sistemaSiembra: 'CUADRADO',
        distanciaPlantas: '3.0',
        distanciaSurcos: '4.0',
        costoJornal: '50.00',
        costoPlanton: '0.80',
        anioInicio: '0',
        anioFin: '1',
    });

    // Actualizar Smart Defaults cuando cambia el distrito
    useEffect(() => {
        if (distrito?.costo_jornal_sugerido) {
            setFormData(prev => ({
                ...prev,
                costoJornal: distrito.costo_jornal_sugerido,
                costoPlanton: distrito.costo_planton_sugerido || '0.80',
            }));
        }
    }, [distrito]);

    // Manejar cambios en los inputs
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    // Construir payload y enviar
    const handleSubmit = (e) => {
        e.preventDefault();

        // Debug: ver valores actuales
        console.log('DEBUG - distrito:', distrito);
        console.log('DEBUG - cultivo:', cultivo);
        console.log('DEBUG - hectareas:', hectareas);

        // Validar datos requeridos
        if (!distrito?.cod_ubigeo) {
            alert('Error: Distrito no seleccionado. Selecciona un distrito en el sidebar.');
            return;
        }

        if (!cultivo?.id) {
            alert('Error: Cultivo no seleccionado. Selecciona un cultivo en el sidebar.');
            return;
        }

        if (!hectareas || hectareas <= 0) {
            alert('Error: Área inválida. Dibuja un polígono válido.');
            return;
        }

        // Validaciones de distancia
        const distPlantas = parseFloat(formData.distanciaPlantas);
        const distSurcos = parseFloat(formData.distanciaSurcos);

        if (isNaN(distPlantas) || distPlantas <= 0) {
            alert('La distancia entre plantas debe ser mayor a 0');
            return;
        }

        if (formData.sistemaSiembra === 'RECTANGULAR' && (isNaN(distSurcos) || distSurcos <= 0)) {
            alert('La distancia entre surcos debe ser mayor a 0');
            return;
        }

        // Construir payload según especificación
        const payload = {
            distrito_id: distrito.cod_ubigeo,
            cultivo_id: cultivo.id,
            hectareas: Math.round(parseFloat(hectareas) * 100) / 100, // Redondear a 2 decimales
            sistema_siembra: formData.sistemaSiembra,
            distanciamiento_largo: distPlantas,
            distanciamiento_ancho: formData.sistemaSiembra === 'RECTANGULAR'
                ? distSurcos
                : distPlantas,
            costo_jornal_usuario: parseFloat(formData.costoJornal) || 50,
            costo_planton_usuario: parseFloat(formData.costoPlanton) || 0.80,
            anio_inicio: parseInt(formData.anioInicio) ?? 0,
            anio_fin: parseInt(formData.anioFin) ?? 1,
        };

        console.log('Enviando payload:', JSON.stringify(payload, null, 2));
        onSubmit(payload);
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content animate-fade-in" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header">
                    <h2 className="modal-title">⚙️ Configuración de Siembra</h2>
                    <p className="modal-subtitle">
                        Área seleccionada: <strong>{hectareas?.toFixed(2)} ha</strong>
                    </p>
                </div>

                {/* Formulario */}
                <form onSubmit={handleSubmit}>
                    {/* Sistema de Siembra */}
                    <div className="form-group">
                        <label className="form-label">Sistema de Siembra</label>
                        <select
                            name="sistemaSiembra"
                            value={formData.sistemaSiembra}
                            onChange={handleChange}
                            className="form-select"
                        >
                            {SISTEMAS_SIEMBRA.map(opt => (
                                <option key={opt.value} value={opt.value}>
                                    {opt.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Distancia entre Plantas */}
                    <div className="form-group">
                        <label className="form-label">Distancia entre plantas (m)</label>
                        <input
                            type="number"
                            name="distanciaPlantas"
                            value={formData.distanciaPlantas}
                            onChange={handleChange}
                            step="0.1"
                            min="0.5"
                            max="20"
                            className="form-input"
                            required
                        />
                    </div>

                    {/* Distancia entre Surcos - Solo visible para RECTANGULAR */}
                    {formData.sistemaSiembra === 'RECTANGULAR' && (
                        <div className="form-group animate-fade-in">
                            <label className="form-label">Distancia entre surcos (m)</label>
                            <input
                                type="number"
                                name="distanciaSurcos"
                                value={formData.distanciaSurcos}
                                onChange={handleChange}
                                step="0.1"
                                min="0.5"
                                max="20"
                                className="form-input"
                                required
                            />
                        </div>
                    )}

                    {/* Divider */}
                    <div className="my-4 border-t border-slate-700"></div>

                    {/* Costos Editables (Smart Defaults) */}
                    <div className="grid grid-cols-2 gap-3">
                        <div className="form-group">
                            <label className="form-label">Costo Jornal (S/.)</label>
                            <input
                                type="number"
                                name="costoJornal"
                                value={formData.costoJornal}
                                onChange={handleChange}
                                step="0.01"
                                min="1"
                                className="form-input"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Costo Plantón (S/.)</label>
                            <input
                                type="number"
                                name="costoPlanton"
                                value={formData.costoPlanton}
                                onChange={handleChange}
                                step="0.01"
                                min="0.01"
                                className="form-input"
                                required
                            />
                        </div>
                    </div>

                    {/* Rango de Años */}
                    <div className="grid grid-cols-2 gap-3">
                        <div className="form-group">
                            <label className="form-label">Año Inicio</label>
                            <input
                                type="number"
                                name="anioInicio"
                                value={formData.anioInicio}
                                onChange={handleChange}
                                min="0"
                                max="10"
                                className="form-input"
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Año Fin</label>
                            <input
                                type="number"
                                name="anioFin"
                                value={formData.anioFin}
                                onChange={handleChange}
                                min="0"
                                max="10"
                                className="form-input"
                                required
                            />
                        </div>
                    </div>

                    {/* Botones */}
                    <div className="flex gap-3 mt-6">
                        <button
                            type="button"
                            onClick={onClose}
                            className="btn-secondary flex-1"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="btn-primary flex-1"
                        >
                            {isLoading ? '⏳ Calculando...' : '🧮 Calcular Costos'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
