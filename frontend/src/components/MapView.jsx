/**
 * MapView - Mapa interactivo con Leaflet
 * 
 * Funcionalidades:
 * - Capa base ESRI Satellite
 * - Herramienta de dibujo de polígonos
 * - Cálculo de área en hectáreas
 */

import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';
import 'leaflet-geometryutil';

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

// Componente para controles de dibujo
function DrawControl({ onPolygonCreated }) {
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
            const layer = e.layer;
            featureGroup.clearLayers();
            featureGroup.addLayer(layer);

            let areaM2 = 0;
            if (e.layerType === 'polygon') {
                const latlngs = layer.getLatLngs()[0];
                areaM2 = L.GeometryUtil.geodesicArea(latlngs);
            }

            const areaHa = areaM2 / 10000;
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
    }, [map, onPolygonCreated]);

    return null;
}

// Centro inicial (Perú - Uchiza, San Martín)
const PERU_CENTER = [-8.46, -76.46];
const DEFAULT_ZOOM = 14;

export default function MapView({ onPolygonCreated }) {
    return (
        <div className="map-container">
            <MapContainer
                center={PERU_CENTER}
                zoom={DEFAULT_ZOOM}
                style={{ height: '100%', width: '100%' }}
                zoomControl={true}
            >
                {/* Capa base ESRI Satellite */}
                <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    attribution='Tiles &copy; Esri'
                />

                {/* Etiquetas */}
                <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
                    attribution=""
                />

                {/* Control de dibujo */}
                <DrawControl onPolygonCreated={onPolygonCreated} />
            </MapContainer>
        </div>
    );
}
