# ESPECIFICACIONES DE UI/UX: DEFINICIONES FALTANTES

**CONTEXTO:**
Complemento al documento `PROMP_MAESTRO_FRONTEND.md`. Aquí se definen los flujos de datos auxiliares y la visualización.

## 1. SELECCIÓN DE CONTEXTO (Distrito y Cultivo)
**Ubicación:** Panel Lateral Izquierdo (Sidebar) o Barra Superior Flotante.
**Mecanismo:**
* **Distrito:** Dropdown (`<select>`).
    * *Data Source:* Para este MVP, usa un array estático en JS con 3 distritos de ejemplo (ej: Uchiza, Tocache, Polvora) y sus IDs.
* **Cultivo:** Dropdown (`<select>`).
    * *Data Source:* Consumir endpoint `/api/cultivos/` (GET). Si no está listo, usar array estático: `[{id: 1, nombre: 'Bolaina'}, {id: 2, nombre: 'Cacao'}]`.

## 2. COSTOS EDITABLES (Smart Defaults)
**Ubicación:** Integrados en el **mismo Modal de Configuración de Siembra** definido anteriormente.
**Lógica:**
* Agregar dos campos adicionales al formulario del Modal:
    1.  `Costo Jornal (S/.)`: Default `50.00`.
    2.  `Costo Plantón (S/.)`: Default `0.80`.
* *UX:* Deben venir pre-llenados (Smart Defaults) para reducir la fricción, pero el usuario puede sobrescribirlos antes de dar click a "Calcular".

## 3. RANGO DE AÑOS
**Ubicación:** Modal de Configuración de Siembra.
**Implementación:**
* Dos inputs numéricos pequeños en una sola fila.
    * `Año Inicio`: Default `0` (Instalación).
    * `Año Fin`: Default `1` (Primer año mantenimiento).
* *Validación:* `Año Fin` debe ser >= `Año Inicio`.

## 4. VISUALIZACIÓN DEL MAPA
**Tecnología sugerida:** Leaflet.js o Mapbox GL JS (a elección del desarrollador).
**Capas (Layers):**
* **Base Layer:** Satellite (Esencial para agricultura). Usa *Esri World Imagery* o *Google Satellite* (si hay API key), si no, *OpenStreetMap* como fallback.
* **Límites:** No cargar GeoJSON de departamentos por ahora (para no sobrecargar). El usuario se ubica visualmente.

## 5. PANTALLA DE RESULTADOS
**Ubicación:** Panel Lateral Izquierdo (Sidebar) - Se despliega o actualiza al recibir respuesta de la API.
**Componentes Visuales:**
1.  **Tarjetas de Resumen (KPIs):**
    * Costo Total Proyecto.
    * Densidad Real (Plantas/Ha).
2.  **Tabla de Desglose:**
    * Columnas: `Actividad`, `Cantidad`, `Costo Total`.
    * Agrupación: Pestañas o Acordeón por `Año` (Año 0, Año 1).
3.  **Botón de Acción:** "Exportar PDF" (Solo visual, sin lógica backend por ahora).

## RESUMEN DEL FLUJO DE USUARIO (User Journey)
1.  Usuario selecciona **Cultivo** y **Distrito** en el Sidebar.
2.  Usuario dibuja un **Polígono** en el mapa.
3.  **EVENTO:** Se abre el **Modal de Configuración**.
    * Usuario elige "Sistema de Siembra" (Rectangular/Cuadrado).
    * Usuario confirma/edita Costos Unitarios y Años.
    * Click en "CALCULAR".
4.  Sistema envía JSON al Backend.
5.  Backend responde.
6.  Sidebar muestra **Tabla de Resultados** y KPIs.