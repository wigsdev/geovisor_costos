# Geovisor Costos Forestales - Roadmap

## Visión del Proyecto
Sistema web para calcular costos de establecimiento de plantaciones forestales en Perú, integrando información geográfica con datos técnicos y económicos.

---

## 🏁 Versión 1.0 - MVP (Actual)
**Estado:** En desarrollo  
**Fecha objetivo:** Diciembre 2024

### Características
- ✅ Selección geográfica (Departamento → Provincia → Distrito)
- ✅ Visualización de capas TopoJSON
- ✅ Dibujo de polígonos de plantación
- ✅ Cálculo de costos por hectárea
- ✅ Modal de configuración (sistema de siembra, distanciamientos)
- ✅ Resumen de costos por año
- ✅ Factores de ajuste (densidad, pendiente)

---

## 🚀 Versión 1.1 - Mejoras UX (Actual)
**Estado:** Completado ✅  
**Fecha:** Diciembre 2024

### Características Implementadas
- ✅ Nueva Barra Lateral unificada
- ✅ Configuración avanzada de geometría (3 Bolillo, Rectangular)
- ✅ Selección de rango de años (Instalación vs Proyecto)
- ✅ Validaciones de backend (decimales, integridad)
- ✅ Persistencia de polígono al recalcular

---

## 📊 Versión 1.2 - Reportes (Actual)
**Estado:** Completado ✅  
**Fecha:** Diciembre 2024

### Características Implementadas
- ✅ Exportar resultados a PDF (Cliente-side)
- ✅ Lógica Inteligente de Servicios (>10 ha)
- ✅ Sistema de Diseño y Paleta de Colores
- ✅ Flujo de edición mejorado (Editar vs Nuevo)


---

## 🛠️ Versión 1.3 - Flexibilidad y Datos (Próxima)
**Estado:** Planificado (Prioridad Alta)
**Objetivo:** Permitir múltiples formas de entrada de datos y enriquecer el análisis.

### 1. Flexibilidad de Entrada (Solicitado)
- [ ] **Modo Manual (Sin Mapa):**
    - Opción para ingresar hectáreas manualmente (input numérico).
    - Selección obligatoria de Ubicación (Dep/Prov/Dist) mediante selectores.
    - Ideal para cotizaciones rápidas sin geometría.
- [ ] **Carga de Archivos (Upload):**
    - Soporte para subir archivos `.geojson`, `.kml`, `.zip` (shapefile).
    - **Backend:** Detectar automáticamente la ubicación (Distrito) basada en el centroide del polígono subido.
    - **Frontend:** Visualizar el polígono cargado y autocompletar el formulario.

### 2. Análisis Económico (Recomendado)
- [ ] **Indicadores Financieros:**
    - Calcular VAN (Valor Actual Neto) y TIR (Tasa Interna de Retorno).
    - Proyección de ingresos basada en precio de madera (configurable).
    - Flujo de Caja simple.

### 3. Mejoras en Reportes
- [ ] **Mapa en PDF:** Incluir captura de pantalla del polígono en el reporte PDF.
- [ ] **Desglose de Costos:** Gráficos de pastel (Highcharts/Chart.js) en el reporte.

---

## 💾 Versión 1.4 - Persistencia y Cuentas
**Estado:** Planificado
**Objetivo:** Gestión de usuarios y proyectos.

### Características
- [ ] Sistema de autenticación (Login/Registro).
- [ ] Guardar proyectos (Mis Cotizaciones).
- [ ] Comparador de Escenarios (Ej: Teca vs Pino en el mismo terreno).
- [ ] Compartir resultados (Link público de solo lectura).

## 🌐 Versión 2.0 - Producción
**Estado:** Planificado  
**Fecha objetivo:** Q2 2025

### Características
- [ ] Despliegue en servidor de producción
- [ ] Optimización de rendimiento
- [ ] CDN para capas TopoJSON
- [ ] Monitoreo y analytics
- [ ] Documentación de usuario final
