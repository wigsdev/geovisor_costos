# 🌲 GEOVISOR DE COSTOS FORESTALES

Sistema de visualización geoespacial para el análisis y cálculo de costos de producción en el sector forestal peruano.

## 📋 Descripción

Este proyecto integra tecnologías de **Sistemas de Información Geográfica (SIG)** con herramientas de análisis de datos para proporcionar:

- Visualización interactiva de parcelas y zonas forestales
- Cálculo automatizado de costos de producción por especie
- Análisis geoespacial de factores que afectan la rentabilidad
- Dashboard con indicadores clave del sector forestal

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| **Backend** | Python 3.x, Django |
| **Frontend** | React, Leaflet/MapLibre |
| **Base de Datos** | PostgreSQL + PostGIS |
| **Geoespacial** | GDAL, GeoPandas, Shapely |

## 📦 Instalación

### Requisitos Previos

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ con extensión PostGIS
- Git

### Backend (Django)

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/geovisor_costos.git
cd geovisor_costos

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o en Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Aplicar migraciones
python manage.py migrate

# Ejecutar servidor de desarrollo
python manage.py runserver
```

### Frontend (React)

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev
```

## 📄 Licencia

Este proyecto está bajo desarrollo. Licencia por definir.

---

*Desarrollado para el análisis forestal del Perú 🇵🇪*
