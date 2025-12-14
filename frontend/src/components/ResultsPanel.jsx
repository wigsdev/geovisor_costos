/**
 * ResultsPanel - Panel de Resultados del Cálculo
 * 
 * Muestra:
 * - Tarjeta de Contexto (Distrito, Cultivo, Área)
 * - KPIs (Costo Total, Densidad)
 * - Tabla de desglose por año
 * - Botón Exportar PDF (placeholder)
 */

export default function ResultsPanel({ results, onClear, onRecalculate, distrito, cultivo, hectareas }) {
    if (!results) return null;

    const {
        costo_total_proyecto,
        factor_densidad,
        factor_pendiente,
        densidad_usuario,
        sistema_siembra,
        resumen_anual,
        detalle_actividades
    } = results;

    return (
        <div className="animate-fade-in">
            {/* Tarjeta de Contexto */}
            <div className="info-card mb-4">
                <div className="grid grid-cols-3 gap-2 text-center">
                    <div>
                        <div className="text-xs text-slate-500 uppercase">Distrito</div>
                        <div className="text-sm font-medium text-white truncate">{distrito?.nombre || 'N/A'}</div>
                    </div>
                    <div>
                        <div className="text-xs text-slate-500 uppercase">Cultivo</div>
                        <div className="text-sm font-medium text-emerald-400">{cultivo?.nombre || 'N/A'}</div>
                    </div>
                    <div>
                        <div className="text-xs text-slate-500 uppercase">Área</div>
                        <div className="text-sm font-medium text-white">{hectareas?.toFixed(2) || '0'} ha</div>
                    </div>
                </div>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="kpi-card">
                    <div className="kpi-currency">S/</div>
                    <div className="kpi-value">{parseFloat(costo_total_proyecto).toLocaleString('es-PE', { minimumFractionDigits: 2 })}</div>
                    <div className="kpi-label">Costo Total Proyecto</div>
                </div>
                <div className="kpi-card">
                    <div className="kpi-value">{densidad_usuario}</div>
                    <div className="kpi-label">Plantas/Ha</div>
                </div>
            </div>

            {/* Factores Aplicados */}
            <div className="result-card mb-4">
                <h4 className="text-sm font-medium text-slate-400 mb-2">Factores Aplicados</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <span className="text-slate-500">Sistema:</span>{' '}
                        <span className="text-white">{sistema_siembra}</span>
                    </div>
                    <div>
                        <span className="text-slate-500">F. Densidad:</span>{' '}
                        <span className="text-emerald-400">{parseFloat(factor_densidad).toFixed(4)}</span>
                    </div>
                    <div>
                        <span className="text-slate-500">F. Pendiente:</span>{' '}
                        <span className="text-amber-400">{parseFloat(factor_pendiente).toFixed(2)}</span>
                    </div>
                </div>
            </div>

            {/* Resumen por Año */}
            <div className="result-card">
                <h4 className="text-sm font-medium text-slate-400 mb-3">Resumen por Año</h4>

                {resumen_anual?.map((anio, idx) => (
                    <div key={idx} className="year-tab">
                        <div className="year-tab-header">
                            <span className="font-medium">
                                {anio.anio === 0 ? '📅 Año 0 (Instalación)' : `📅 Año ${anio.anio}`}
                            </span>
                            <span className="text-emerald-400 font-bold">
                                S/ {parseFloat(anio.total).toLocaleString('es-PE', { minimumFractionDigits: 2 })}
                            </span>
                        </div>
                        <div className="year-tab-content">
                            <div className="grid grid-cols-3 gap-2 text-xs text-slate-400">
                                <div>
                                    <span className="block text-slate-500">Mano Obra</span>
                                    S/ {parseFloat(anio.mano_obra).toFixed(2)}
                                </div>
                                <div>
                                    <span className="block text-slate-500">Insumos</span>
                                    S/ {parseFloat(anio.insumos).toFixed(2)}
                                </div>
                                <div>
                                    <span className="block text-slate-500">Servicios</span>
                                    S/ {parseFloat(anio.servicios).toFixed(2)}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Botones de Acción */}
            <div className="flex flex-col gap-2 mt-4">
                <button onClick={onRecalculate} className="btn-primary w-full">
                    📊 Recalcular (mismo polígono)
                </button>
                <div className="flex gap-2">
                    <button onClick={onClear} className="btn-secondary flex-1">
                        🔄 Nuevo
                    </button>
                    <button className="btn-secondary flex-1" disabled title="Próximamente">
                        📄 PDF
                    </button>
                </div>
            </div>
        </div>
    );
}
