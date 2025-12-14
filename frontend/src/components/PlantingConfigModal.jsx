/**
 * PlantingConfigModal - Modal de Configuración de Plantación
 */

import { useState, useEffect } from 'react';

export default function PlantingConfigModal({
    isOpen,
    onClose,
    onSubmit,
    hectareas,
    distrito,
    cultivo,
    isLoading
}) {
    const [densidad, setDensidad] = useState(1111);
    const [sistema, setSistema] = useState('cuadrado');
    const [pendiente, setPendiente] = useState(0);
    const [costoJornal, setCostoJornal] = useState(50);
    const [costoPlanton, setCostoPlanton] = useState(0.80);
    const [anioInicio, setAnioInicio] = useState(1);
    const [anioFin, setAnioFin] = useState(8);

    useEffect(() => {
        if (cultivo) setDensidad(cultivo.densidad_base || 1111);
        if (cultivo) setAnioFin(cultivo.turno_estimado || 8);
        if (distrito) {
            setCostoJornal(parseFloat(distrito.costo_jornal_sugerido) || 50);
            setCostoPlanton(parseFloat(distrito.costo_planton_sugerido) || 0.80);
            setPendiente(distrito.pendiente_promedio_estimada || 0);
        }
    }, [cultivo, distrito]);

    if (!isOpen) return null;

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({
            cod_ubigeo: distrito?.cod_ubigeo,
            cultivo_id: cultivo?.id,
            hectareas: parseFloat(hectareas),
            densidad: parseInt(densidad),
            sistema_siembra: sistema,
            porcentaje_pendiente: parseInt(pendiente),
            costo_jornal: parseFloat(costoJornal),
            costo_planton: parseFloat(costoPlanton),
            anio_inicio: parseInt(anioInicio),
            anio_fin: parseInt(anioFin)
        });
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">⚙️ Configuración de Plantación</h2>
                    <p className="modal-subtitle">
                        {distrito?.nombre} • {cultivo?.nombre} • {hectareas?.toFixed(2)} ha
                    </p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="form-group">
                            <label className="form-label">Área (ha)</label>
                            <input type="number" value={hectareas?.toFixed(2) || 0} className="form-input" disabled />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Densidad (plantas/ha)</label>
                            <input type="number" value={densidad} onChange={e => setDensidad(e.target.value)} className="form-input" min="100" max="10000" />
                        </div>
                    </div>

                    <div className="form-group mb-4">
                        <label className="form-label">Sistema de Siembra</label>
                        <div className="flex gap-4">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="radio" name="sistema" value="cuadrado" checked={sistema === 'cuadrado'} onChange={e => setSistema(e.target.value)} />
                                <span className="text-slate-300">Cuadrado</span>
                            </label>
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="radio" name="sistema" value="tresbolillo" checked={sistema === 'tresbolillo'} onChange={e => setSistema(e.target.value)} />
                                <span className="text-slate-300">Tresbolillo</span>
                            </label>
                        </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="form-group">
                            <label className="form-label">% Pendiente</label>
                            <input type="number" value={pendiente} onChange={e => setPendiente(e.target.value)} className="form-input" min="0" max="100" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Jornal (S/)</label>
                            <input type="number" value={costoJornal} onChange={e => setCostoJornal(e.target.value)} className="form-input" step="0.01" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Plantón (S/)</label>
                            <input type="number" value={costoPlanton} onChange={e => setCostoPlanton(e.target.value)} className="form-input" step="0.01" />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="form-group">
                            <label className="form-label">Año Inicio</label>
                            <input type="number" value={anioInicio} onChange={e => setAnioInicio(e.target.value)} className="form-input" min="1" max="20" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Año Fin</label>
                            <input type="number" value={anioFin} onChange={e => setAnioFin(e.target.value)} className="form-input" min="1" max="30" />
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <button type="button" onClick={onClose} className="btn-secondary flex-1">
                            Cancelar
                        </button>
                        <button type="submit" className="btn-primary flex-1" disabled={isLoading}>
                            {isLoading ? '⏳ Calculando...' : '📊 Calcular Costos'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
