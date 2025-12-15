# Geovisor Costos Forestales - Task List

## Estado: En Desarrollo Activo
**Última actualización:** 2024-12-14

---

## Fase 1: Infraestructura Base ✅

- [x] Configurar proyecto Django (backend)
- [x] Configurar proyecto Vite + React (frontend)
- [x] Crear modelos de datos (Distrito, Cultivo, PaqueteTecnológico)
- [x] Implementar API REST con Django REST Framework
- [x] Configurar CORS para desarrollo local
- [x] Cargar datos iniciales (fixtures)

---

## Fase 2: Interfaz de Usuario ✅

- [x] Diseñar layout principal (Sidebar + MapView)
- [x] Implementar tema oscuro con CSS puro
- [x] Crear selectores en cascada (Departamento → Provincia → Distrito)
- [x] Implementar selector de cultivo forestal
- [x] Diseñar panel de resultados con KPIs
- [x] Estilizar tarjetas de resumen anual

---

## Fase 3: Integración de Mapa ✅

- [x] Integrar Leaflet con React-Leaflet
- [x] Configurar capa base ESRI Satellite
- [x] Implementar herramienta de dibujo de polígonos
- [x] Calcular área de polígonos en hectáreas
- [x] Fix para iconos y bugs de Leaflet 1.9+

---

## Fase 4: Capas Geográficas TopoJSON ✅

- [x] Integrar topojson-client
- [x] Cargar departamentos al inicio (7 departamentos del proyecto)
- [x] Mostrar provincias al seleccionar departamento
- [x] Mostrar distritos al seleccionar provincia
- [x] Zoom automático según nivel de selección
- [x] Estilos diferenciados por nivel (verde/naranja/cyan)

---

## Fase 5: Lógica de Negocio ✅

- [x] Implementar cálculo de costos en backend
- [x] Aplicar factores (densidad, pendiente)
- [x] Generar resumen anual de costos
- [x] Modal de configuración de plantación
- [x] Validar selecciones antes de dibujar

---

## Fase 6: Mejoras de UX 🔄

- [x] Placeholders en selectores
- [x] Restricción de dibujo sin selecciones completas
- [x] Estilos de Leaflet Draw para tema oscuro
- [ ] Tooltips informativos en controles
- [ ] Animaciones de carga

---

## Fase 7: Documentación 🔄

- [x] Crear carpeta docs
- [x] Documentar API endpoints
- [x] Documentar componentes frontend
- [x] Crear roadmap
- [x] Documentar mejoras futuras
- [ ] README principal actualizado

---

## Backlog (Mejoras Futuras)

- [ ] Detección automática de ubicación por polígono
- [ ] Geolocalización del usuario
- [ ] Exportar resultados a PDF
- [ ] Guardar/cargar proyectos
- [ ] Múltiples polígonos por proyecto
- [ ] Comparación de cultivos
