# Changelog

## [1.3.1] - 2024-12-14
### Refactorización
- **Lógica de Años:** Se ha separado conceptual y técnicamente la fase de "Instalación" (Año 0) de la fase de "Mantenimiento" (Año 1+).
- **API:** La respuesta de `calcular-costos` ahora devuelve un objeto `costos_instalacion` independiente y el array `resumen_anual` inicia estrictamente en el año 1.

## [1.3.1] - 2024-12-14
### Refactorización
- **Lógica de Años:** Se ha separado conceptual y técnicamente la fase de "Instalación" (Año 0) de la fase de "Mantenimiento" (Año 1+).
- **API:** La respuesta de `calcular-costos` ahora devuelve un objeto `costos_instalacion` independiente y el array `resumen_anual` inicia estrictamente en el año 1.

## [1.3.0] - 2024-12-14

### Added
- **Modo Manual:** Opción para ingresar hectáreas directamente sin dibujar polígonos, facilitando cotizaciones rápidas.
- **Análisis Financiero:**
  - Cálculo de **VAN** (Valor Actual Neto) con tasa de descuento del 10%.
  - Cálculo de **TIR** (Tasa Interna de Retorno).
  - Cálculo de **Ratio B/C** (Beneficio/Costo).
  - Proyección de **Flujo de Caja** a 20 años.
- **Ubicación Escalable:** Nuevo comando `import_coords_topojson` que extrae centroides de distritos desde el mapa TopoJSON para corregir la detección de ubicación en producción (backend).
- **Carga de Archivos:** Soporte mejorado para subir archivos KML/ZIP.
- **Reportes PDF:** Inclusión de tabla de flujo de caja y nuevos KPIs financieros.

### Fixed
- **Detección de Ubicación:** Solucionado error en producción donde distritos sin coordenadas en BD (como Uchiza) defaulting a Ancash.
- **Mapa:** Mejoras en la persistencia del polígono al cambiar filtros.

## [1.2.0] - 2024-12-10

### Added
- Exportación a PDF (jspdf).
- Lógica de "Servicios Inteligentes" (>10 ha).
- Nuevo sistema de diseño y paleta de colores.
- Tooltips nativos y mejoras de UX en dibujo.

## [1.1.0] - 2024-12-01

### Added
- Configuración avanzada de geometría (Tres Bolillo).
- Selección de rango de años.
- Nueva barra lateral unificada.

## [1.0.0] - 2024-11-20

### Added
- Lanzamiento inicial (MVP).
- Funcionalidades base de mapa, costos y configuración.
