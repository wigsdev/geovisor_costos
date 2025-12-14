/**
 * ResultsPanel - Panel de Resultados del Cálculo
 */

export default function ResultsPanel({ results, onClear, onRecalculate }) {
    if (!results) return null;

    const {
        costo_total_proyecto,
        factor_densidad,
        factor_pendiente,
        densidad_usuario,
        sistema_siembra,
        resumen_anual
    } = results;

    return (
        <div className="animate-fade-in">
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="kpi-card">
                    <div className="kpi-value">S/ {parseFloat(costo_total_proyecto).toLocaleString('es-PE', { minimumFractionDigits: 2 })}</div>
                    <div className="kpi-label">Costo Total Proyecto</div>
                </div>
                <div className="kpi-card">
                    <div className="kpi-value">{densidad_usuario}</div>
                    <div className="kpi-label">Plantas/Ha</div>
                </div>
            </div>

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
                        <span className="text-emerald-400">{parseFloat(factor_pendiente).toFixed(2)}</span>
                    </div>
                </div>
            </div>

            <div className="result-card mb-4">
                <h4 className="text-sm font-medium text-slate-400 mb-3">Costos por Año</h4>
                <table className="results-table">
                    <thead>
                        <tr>
                            <th>Año</th>
                            <th>Instalación</th>
                            <th>Mantenimiento</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {resumen_anual?.map((item, idx) => (
                            <tr key={idx}>
                                <td className="text-white font-medium">{item.anio}</td>
                                <td className="text-slate-300">S/ {parseFloat(item.instalacion).toLocaleString('es-PE')}</td>
                                <td className="text-slate-300">S/ {parseFloat(item.mantenimiento).toLocaleString('es-PE')}</td>
                                <td className="text-emerald-400 font-medium">S/ {parseFloat(item.total).toLocaleString('es-PE')}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="flex gap-2">
                <button onClick={onClear} className="btn-secondary flex-1">
                    🔄 Nuevo Cálculo
                </button>
                <button onClick={onRecalculate} className="btn-secondary flex-1">
                    ♻️ Recalcular
                </button>
            </div>
        </div>
    );
}
