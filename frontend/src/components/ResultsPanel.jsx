/**
 * ResultsPanel - Panel de Resultados del Cálculo
 * 
 * Muestra:
 * - Tarjeta de Contexto (Distrito, Cultivo, Área)
 * - KPIs (Costo Total, Densidad)
 * - Tabla de desglose por año
 * - Botón Exportar PDF (placeholder)
 */

import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export default function ResultsPanel({ results, onClear, onReset, onRecalculate, distrito, cultivo, hectareas }) {
    if (!results) return null;

    const {
        costo_total_proyecto,
        factor_densidad,
        factor_pendiente,
        densidad_usuario,
        sistema_siembra,
        resumen_anual,
        // Nuevos KPIs Financieros
        van,
        ratio_beneficio_costo,
        ingreso_total_estimado
    } = results;

    const handleExportPDF = () => {
        const doc = new jsPDF();
        const pageWidth = doc.internal.pageSize.width;

        // Header
        doc.setFontSize(18);
        doc.setTextColor(16, 185, 129); // Emerald-500
        doc.text('Geovisor Costos Forestales', 14, 20);

        doc.setFontSize(10);
        doc.setTextColor(100);
        doc.text(`Fecha: ${new Date().toLocaleDateString()}`, pageWidth - 14, 20, { align: 'right' });

        // Project Info
        doc.setFontSize(12);
        doc.setTextColor(0);
        doc.text(`Ubicacion: ${distrito?.nombre || 'N/A'}`, 14, 30);
        doc.text(`Cultivo: ${cultivo?.nombre || 'N/A'}`, 14, 37);
        doc.text(`Area: ${hectareas?.toFixed(2)} ha`, 14, 44);
        doc.text(`Sistema: ${sistema_siembra}`, 14, 51);

        // Financial KPIs
        doc.setFontSize(11);
        doc.setTextColor(50);
        doc.text(`VAN: S/ ${parseFloat(van).toLocaleString('es-PE', { minimumFractionDigits: 2 })}`, 140, 30);
        doc.text(`B/C: ${parseFloat(ratio_beneficio_costo).toFixed(2)}`, 140, 37);

        doc.setFillColor(240, 253, 244); // Light Emerald bg
        doc.roundedRect(14, 60, pageWidth - 28, 20, 3, 3, 'F');

        doc.setFontSize(14);
        doc.setTextColor(0);
        doc.text(`Costo Total: S/ ${parseFloat(costo_total_proyecto).toLocaleString('es-PE', { minimumFractionDigits: 2 })}`, 20, 73);
        doc.setFontSize(11);
        doc.text(`Densidad: ${densidad_usuario} pl/ha`, pageWidth - 20, 73, { align: 'right' });

        // Table
        const tableData = resumen_anual.map(r => [
            r.anio === 0 ? 'Año 0 (Instalación)' : `Año ${r.anio}`,
            `S/ ${parseFloat(r.mano_obra).toLocaleString('es-PE', { minimumFractionDigits: 2 })}`,
            `S/ ${parseFloat(r.insumos).toLocaleString('es-PE', { minimumFractionDigits: 2 })}`,
            `S/ ${parseFloat(r.servicios).toLocaleString('es-PE', { minimumFractionDigits: 2 })}`,
            `S/ ${parseFloat(r.total).toLocaleString('es-PE', { minimumFractionDigits: 2 })}`
        ]);

        autoTable(doc, {
            startY: 90,
            head: [['Año', 'Mano de Obra', 'Insumos', 'Servicios', 'Total']],
            body: tableData,
            headStyles: { fillColor: [16, 185, 129] }, // Emerald header
            theme: 'grid',
            styles: { fontSize: 10 },
        });

        // Footer
        const finalY = doc.lastAutoTable.finalY + 10;
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text('Generado por Geovisor v1.2', 14, doc.internal.pageSize.height - 10);

        doc.save(`Presupuesto_${distrito?.nombre || 'Proyecto'}.pdf`);
    };

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

            {/* KPIs Financieros (Nuevo v1.3) */}
            <div className="grid grid-cols-3 gap-2 mb-4">
                <div className={`kpi-card ${van > 0 ? 'border-emerald-500/50' : 'border-red-500/50'}`}>
                    <div className="kpi-value text-base flex flex-col items-center justify-center leading-tight">
                        <span className="text-[10px] text-emerald-500/80 font-normal mb-0.5">S/</span>
                        <span>{parseFloat(van).toLocaleString('es-PE', { maximumFractionDigits: 0 })}</span>
                    </div>
                    <div className="kpi-label text-[9px] mt-1">VAN (Estimado)</div>
                </div>
                <div className="kpi-card">
                    <div className="kpi-value text-base flex flex-col items-center justify-center leading-tight mt-[15px]">
                        <span>{parseFloat(ratio_beneficio_costo).toFixed(2)}</span>
                    </div>
                    <div className="kpi-label text-[9px] mt-1">B / C</div>
                </div>
                <div className="kpi-card">
                    <div className="kpi-value text-base text-emerald-400 flex flex-col items-center justify-center leading-tight">
                        <span className="text-[10px] text-emerald-500/80 font-normal mb-0.5">S/</span>
                        <span>{parseFloat(ingreso_total_estimado).toLocaleString('es-PE', { maximumFractionDigits: 0 })}</span>
                    </div>
                    <div className="kpi-label text-[9px] mt-1">Ingreso Bruto</div>
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
                            <span className="text-white font-medium">
                                {anio.anio === 0 ? '📅 Año 0 (Instalación)' : `📅 Año ${anio.anio}`}
                            </span>
                            <span className="text-emerald-400 font-bold text-lg">
                                S/ {parseFloat(anio.total).toLocaleString('es-PE', { minimumFractionDigits: 2 })}
                            </span>
                        </div>
                        <div className="year-tab-content">
                            <div className="grid grid-cols-3 gap-3">
                                <div className="year-cost-item">
                                    <span className="year-cost-label">Mano de Obra</span>
                                    <span className="year-cost-value text-cyan-400">
                                        S/ {parseFloat(anio.mano_obra).toLocaleString('es-PE', { minimumFractionDigits: 2 })}
                                    </span>
                                </div>
                                <div className="year-cost-item">
                                    <span className="year-cost-label">Insumos</span>
                                    <span className="year-cost-value text-amber-400">
                                        S/ {parseFloat(anio.insumos).toLocaleString('es-PE', { minimumFractionDigits: 2 })}
                                    </span>
                                </div>
                                <div className="year-cost-item">
                                    <span className="year-cost-label">Servicios</span>
                                    <span className="year-cost-value text-purple-400">
                                        S/ {parseFloat(anio.servicios).toLocaleString('es-PE', { minimumFractionDigits: 2 })}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Botones de Acción */}
            {/* Botones de Acción */}
            <div className="flex flex-col gap-2 mt-4">
                <button
                    onClick={handleExportPDF}
                    className="btn-secondary w-full bg-slate-700 hover:bg-slate-600 border-none text-white font-bold py-2 mb-2"
                >
                    📄 Exportar Reporte PDF
                </button>

                <div className="grid grid-cols-2 gap-2">
                    <button
                        onClick={onClear}
                        className="btn-primary flex items-center justify-center gap-1 bg-emerald-600 hover:bg-emerald-500"
                        title="Modificar parámetros manteniendo el polígono"
                    >
                        ✏️ Editar
                    </button>
                    <button
                        onClick={onReset}
                        className="btn-secondary flex items-center justify-center gap-1 bg-amber-700 hover:bg-amber-600 border-none text-white"
                        title="Borrar todo y empezar de nuevo"
                    >
                        🗑️ Nuevo
                    </button>
                </div>
            </div>
        </div>
    );
}
