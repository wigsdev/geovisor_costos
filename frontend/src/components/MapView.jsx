/**
 * MapView - Mapa interactivo con Leaflet
 * 
 * Funcionalidades:
 * - Capa base ESRI Satellite
 * - Herramienta de dibujo de polígonos
 * - Capas geográficas TopoJSON con zoom automático
 */

import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet-geometryutil';
import * as topojson from 'topojson-client';

// Fix para bug de leaflet-draw con Leaflet 1.9+
if (L.Draw && L.Draw.Polygon) {
    const originalGetMeasurementString = L.Draw.Polygon.prototype._getMeasurementString;
    L.Draw.Polygon.prototype._getMeasurementString = function () {
        try {
            return originalGetMeasurementString.call(this);
        } catch (e) {
            return '';
        }
    };
}

if (L.Draw && L.Draw.Polyline) {
    const originalGetMeasurementString = L.Draw.Polyline.prototype._getMeasurementString;
    L.Draw.Polyline.prototype._getMeasurementString = function () {
        try {
            return originalGetMeasurementString.call(this);
        } catch (e) {
            return '';
        }
    };
}

// Fix para iconos de Leaflet en Vite
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Cache para TopoJSON
const topoCache = {};

// 7 Departamentos del proyecto
const DEPARTAMENTOS_PROYECTO = [
    'ANCASH', 'SAN MARTIN', 'CAJAMARCA',
    'MADRE DE DIOS', 'HUANUCO', 'JUNIN', 'PASCO'
];

// Cargar TopoJSON con cache
async function loadTopoJSON(url) {
    if (topoCache[url]) {
        return topoCache[url];
    }
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        topoCache[url] = data;
        return data;
    } catch (error) {
        console.error('Error cargando TopoJSON:', url, error);
        return null;
    }
}

// Componente para mostrar capas geográficas y hacer zoom
function GeoLayers({ selectedDepartamento, selectedProvincia, selectedDistrito }) {
    const map = useMap();
    const geoLayerRef = useRef(null);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const loadAndDisplay = async () => {
            setIsLoading(true);

            // Limpiar capa anterior
            if (geoLayerRef.current) {
                map.removeLayer(geoLayerRef.current);
                geoLayerRef.current = null;
            }

            let topoUrl = null;
            let objectName = null;
            let filterFn = null;

            // Determinar qué nivel mostrar
            if (selectedDistrito?.nombre) {
                // Nivel distrito - zoom al distrito seleccionado
                topoUrl = '/geo/DISTRITOS_PI7.topojson';
                objectName = 'DISTRITOS_PI7';
                filterFn = (props) =>
                    props.NOM_DEP === selectedDepartamento &&
                    props.NOM_PRO === selectedProvincia &&
                    props.NOM_DIST === selectedDistrito.nombre;
            } else if (selectedProvincia) {
                // Nivel provincia - zoom a la provincia seleccionada
                topoUrl = '/geo/PROVINCIAS_PI7.topojson';
                objectName = 'PROVINCIAS_PI7';
                filterFn = (props) =>
                    props.NOM_DEP === selectedDepartamento &&
                    props.NOM_PROV === selectedProvincia;
            } else if (selectedDepartamento) {
                // Nivel departamento - zoom al departamento seleccionado
                topoUrl = '/geo/DEPARTAMENTOS_PI7.topojson';
                objectName = 'DEPARTAMENTOS_PI7';
                filterFn = (props) => props.NOM_DEP === selectedDepartamento;
            } else {
                // Vista inicial - mostrar los 7 departamentos
                topoUrl = '/geo/DEPARTAMENTOS_PI7.topojson';
                objectName = 'DEPARTAMENTOS_PI7';
                filterFn = (props) => DEPARTAMENTOS_PROYECTO.includes(props.NOM_DEP);
            }

            try {
                const topoData = await loadTopoJSON(topoUrl);
                if (!topoData) {
                    setIsLoading(false);
                    return;
                }

                // Convertir TopoJSON a GeoJSON
                const geoJson = topojson.feature(topoData, topoData.objects[objectName]);

                // Filtrar las características
                const filteredFeatures = geoJson.features.filter(f => filterFn(f.properties));

                if (filteredFeatures.length === 0) {
                    console.warn('No se encontró la característica:', selectedDepartamento, selectedProvincia, selectedDistrito?.nombre);
                    setIsLoading(false);
                    return;
                }

                const filteredGeoJson = {
                    type: 'FeatureCollection',
                    features: filteredFeatures
                };

                // Estilo según nivel - colores diferentes para cada nivel
                const isInitialView = !selectedDepartamento;
                let style;

                if (selectedDistrito?.nombre) {
                    // Nivel distrito - cyan/turquesa
                    style = {
                        color: '#06b6d4',
                        weight: 3,
                        fillColor: '#06b6d4',
                        fillOpacity: 0.2
                    };
                } else if (selectedProvincia) {
                    // Nivel provincia - naranja/amber
                    style = {
                        color: '#f59e0b',
                        weight: 2.5,
                        fillColor: '#f59e0b',
                        fillOpacity: 0.15
                    };
                } else if (selectedDepartamento) {
                    // Nivel departamento seleccionado - verde brillante
                    style = {
                        color: '#22c55e',
                        weight: 2,
                        fillColor: '#22c55e',
                        fillOpacity: 0.12
                    };
                } else {
                    // Vista inicial - 7 departamentos
                    style = {
                        color: '#10b981',
                        weight: 1.5,
                        fillColor: '#10b981',
                        fillOpacity: 0.08
                    };
                }

                // Crear capa
                const layer = L.geoJSON(filteredGeoJson, {
                    style: style,
                    onEachFeature: (feature, layer) => {
                        // Tooltip con nombre
                        const props = feature.properties;
                        const name = props.NOM_DIST || props.NOM_PROV || props.NOM_DEP;
                        layer.bindTooltip(name, {
                            permanent: false,
                            direction: 'center',
                            className: 'geo-tooltip'
                        });
                    }
                }).addTo(map);

                geoLayerRef.current = layer;

                // Zoom a los límites
                const bounds = layer.getBounds();
                if (bounds.isValid()) {
                    const maxZoom = selectedDistrito ? 13 : (selectedProvincia ? 11 : (selectedDepartamento ? 9 : 6));
                    map.fitBounds(bounds, {
                        padding: [30, 30],
                        maxZoom: maxZoom,
                        animate: true
                    });
                }
            } catch (error) {
                console.error('Error procesando TopoJSON:', error);
            }

            setIsLoading(false);
        };

        loadAndDisplay();
    }, [map, selectedDepartamento, selectedProvincia, selectedDistrito]);

    return null;
}

// Componente para controles de dibujo
function DrawControl({ onPolygonCreated, canDraw }) {
    const map = useMap();
    const featureGroupRef = useRef(null);
    const drawControlRef = useRef(null);

    useEffect(() => {
        if (drawControlRef.current) return;

        const featureGroup = L.featureGroup().addTo(map);
        featureGroupRef.current = featureGroup;

        const drawControl = new L.Control.Draw({
            position: 'topright',
            draw: {
                polygon: {
                    allowIntersection: false,
                    showArea: true,
                    shapeOptions: {
                        color: '#10b981',
                        weight: 3,
                        fillColor: '#10b981',
                        fillOpacity: 0.3
                    }
                },
                polyline: false,
                circle: false,
                circlemarker: false,
                marker: false,
                rectangle: false
            },
            edit: {
                featureGroup: featureGroup,
                remove: true
            }
        });

        map.addControl(drawControl);
        drawControlRef.current = drawControl;

        const onCreated = (e) => {
            // Validar que hay distrito seleccionado
            if (!canDraw) {
                alert('⚠️ Primero debe seleccionar:\n• Departamento\n• Provincia\n• Distrito\n• Cultivo\n\nAntes de dibujar el área de plantación.');
                featureGroup.clearLayers();
                return;
            }

            const layer = e.layer;
            featureGroup.clearLayers();
            featureGroup.addLayer(layer);

            let areaM2 = 0;
            if (e.layerType === 'polygon') {
                const latlngs = layer.getLatLngs()[0];
                areaM2 = L.GeometryUtil.geodesicArea(latlngs);
            }

            // Convertir a hectáreas y redondear a 2 decimales (Backend exige max 2 decimales)
            let areaHa = areaM2 / 10000;
            areaHa = Math.round(areaHa * 100) / 100;
            onPolygonCreated(areaHa, layer);
        };

        const onDeleted = () => {
            onPolygonCreated(null, null);
        };

        map.on(L.Draw.Event.CREATED, onCreated);
        map.on(L.Draw.Event.DELETED, onDeleted);

        return () => {
            map.off(L.Draw.Event.CREATED, onCreated);
            map.off(L.Draw.Event.DELETED, onDeleted);
            if (drawControlRef.current) {
                map.removeControl(drawControlRef.current);
                drawControlRef.current = null;
            }
            if (featureGroupRef.current) {
                map.removeLayer(featureGroupRef.current);
                featureGroupRef.current = null;
            }
        };
    }, [map, onPolygonCreated, canDraw]);

    return null;
}

// Centro inicial (Perú central)
const PERU_CENTER = [-9.19, -75.015];
const DEFAULT_ZOOM = 6;

export default function MapView({
    onPolygonCreated,
    selectedDepartamento,
    selectedProvincia,
    selectedDistrito,
    selectedCultivo
}) {
    // Determinar si puede dibujar (tiene distrito y cultivo seleccionados)
    const canDraw = Boolean(selectedDistrito && selectedCultivo);

    return (
        <div className="map-container">
            <MapContainer
                center={PERU_CENTER}
                zoom={DEFAULT_ZOOM}
                style={{ height: '100%', width: '100%' }}
                zoomControl={true}
            >
                {/* Capa base ESRI World Imagery */}
                <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    attribution='Tiles &copy; Esri'
                />

                {/* Etiquetas */}
                <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                    attribution=""
                />

                {/* Capas geográficas TopoJSON */}
                <GeoLayers
                    selectedDepartamento={selectedDepartamento}
                    selectedProvincia={selectedProvincia}
                    selectedDistrito={selectedDistrito}
                />

                {/* Control de dibujo */}
                <DrawControl
                    onPolygonCreated={onPolygonCreated}
                    canDraw={canDraw}
                />
            </MapContainer>
        </div>
    );
}
