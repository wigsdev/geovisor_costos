# Manual Técnico - Geovisor Costos Forestales v1.1

## 1. Visión General
El **Geovisor de Costos Forestales** es una aplicación web full-stack diseñada para calcular, visualizar y gestionar los costos de proyectos de reforestación en Perú. Combina herramientas SIG (Sistemas de Información Geográfica) con un motor de cálculo financiero ajustado a parámetros técnicos y regionales.

## 2. Arquitectura del Sistema

### 2.1 Stack Tecnológico
- **Backend:** Python + Django (GeoDjango)
- **Base de Datos:** PostgreSQL + PostGIS Extension
- **Frontend:** React + Vite + Leaflet
- **Infraestructura:** Docker + Railway (Producción)

### 2.2 Diagrama de Componentes
```mermaid
graph TD
    Client[Cliente Web (React)] <--> API[API REST (Django REST Framework)]
    API <--> DB[(PostgreSQL + PostGIS)]
    API <--> Logic[Motor de Cálculo]
    Client --> Maps[Capas TopoJSON / ESRI]
```

## 3. Lógica de Negocio (Backend)

### 3.1 Motor de Costos v2.1
El cálculo se basa en la intersección de **Cultivos** y **Zonas Económicas**. 

#### Modelo de Mano de Obra 50/50
Para actividades de instalación sensibles a la densidad (ej. hoyado), el esfuerzo se divide:
- **50% Fijo:** Costo base independiente de la densidad (desplazamientos, preparación).
- **50% Variable:** Costo proporcional a la densidad de plantas (número de hoyos).

Fórmula:
`Jornales = (JornalesBase * 0.5) + (JornalesBase * 0.5 * FactorDensidad)`

#### Factores de Ajuste
1. **Factor Densidad:** `DensidadUsuario / DensidadBase`
2. **Factor Pendiente:** `1.0` a `1.35` según la topografía del distrito (datos cargados previamente).

### 3.2 Modelos de Datos Clave
- **ZonaEconomica:** Agrupa departamentos y define precios referenciales.
- **ParametroMantenimiento:** Define la intensidad de labores (días limpieza/poda) por región.
- **PaqueteTecnologico:** Lista desglosada de actividades (Insumos, M.O., Servicios) por año.

## 4. Frontend (React)

### 4.1 Estructura
- **Sidebar:** Controlador principal del estado (ubicación, cultivo, años, configuración).
- **MapView:** Componente Leaflet aislado. Maneja la lógica geoespacial (dibujo, cálculo de área).
- **ResultsPanel:** Visualizador pasivo de datos recibidos del backend.

### 4.2 Flujo de Datos
1. Usuario selecciona Distrito -> `Sidebar` carga precios y cultivos filtrados.
2. Usuario configura Geometría y Años.
3. Usuario dibuja Polígono -> `MapView` retorna hectáreas (redondeado a 2 decimales).
4. `Sidebar` envía todo al endpoint `/api/calcular-costos/`.

## 5. Scripts de Mantenimiento
- `python manage.py seed_data_v1_1`: Carga/Resetea la BD con datos calibrados (20 combinaciones).
- `python manage.py import_distritos`: Carga el maestro de distritos y geometrías.
