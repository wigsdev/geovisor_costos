# Mejoras Futuras - Geovisor Costos Forestales

## 1. Detección Automática de Ubicación por Polígono

### Descripción
Cuando el usuario dibuja un polígono en el mapa, el sistema detecta automáticamente en qué departamento, provincia y distrito se encuentra, llenando los filtros de ubicación automáticamente.

### Implementación Técnica

1. **Obtener centroide del polígono dibujado**
   ```javascript
   const center = layer.getBounds().getCenter();
   // o usar Turf.js para centroide más preciso
   import { centroid } from '@turf/turf';
   ```

2. **Cargar TopoJSON de distritos**
   - Ya tenemos `DISTRITOS_PI7.topojson` cargado

3. **Test punto-en-polígono**
   ```javascript
   import booleanPointInPolygon from '@turf/boolean-point-in-polygon';
   
   const point = turf.point([lng, lat]);
   const matchedDistrict = distritosGeoJson.features.find(feature => 
     booleanPointInPolygon(point, feature)
   );
   ```

4. **Auto-llenar filtros**
   ```javascript
   if (matchedDistrict) {
     setSelectedDepartamento(matchedDistrict.properties.NOM_DEP);
     setSelectedProvincia(matchedDistrict.properties.NOM_PRO);
     // Buscar el objeto distrito del API
     const distrito = allDistritos.find(d => 
       d.nombre === matchedDistrict.properties.NOM_DIST
     );
     setSelectedDistrito(distrito);
   }
   ```

### Dependencias Requeridas
```bash
npm install @turf/turf
# o solo los módulos necesarios:
npm install @turf/centroid @turf/boolean-point-in-polygon
```

### Beneficios
- Mejor UX: usuario puede dibujar primero
- Detecta ubicación automáticamente
- Reduce errores de selección manual

### Estimación de Esfuerzo
- Complejidad: Moderada
- Tiempo estimado: 2-3 horas

---

## 2. Otras Mejoras Pendientes

### 2.1 Geolocalización del Usuario
- Usar `navigator.geolocation` para centrar mapa en ubicación del usuario

### 2.2 Exportar Resultados a PDF
- Generar reporte en PDF con los costos calculados

### 2.3 Guardar Proyectos
- Permitir guardar y cargar proyectos con polígonos y configuraciones
