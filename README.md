# 🌲 GEOVISOR DE COSTOS FORESTALES

Sistema web para el cálculo y visualización de costos de establecimiento de plantaciones forestales en Perú.

![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow)
![Versión](https://img.shields.io/badge/Versión-1.2.0-blue)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)

## 📋 Descripción

**Geovisor Costos Forestales** integra tecnologías de Sistemas de Información Geográfica (SIG) con herramientas de análisis económico para proporcionar:

- 🗺️ Visualización interactiva de límites administrativos (departamentos, provincias, distritos)
- 📐 Dibujo de polígonos para áreas de plantación
- 💰 Cálculo automatizado de costos por hectárea y por año
- 📄 **Exportación de Reportes PDF** profesionales
- 🤖 **Lógica Inteligente** de asignación de servicios (>10 ha)
- 🌱 Soporte para múltiples especies forestales
- 📊 Factores de ajuste (densidad, pendiente)

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| **Backend** | Python 3.10+, Django 4.2, Django REST Framework |
| **Frontend** | React 18, Vite, CSS puro |
| **Mapas** | Leaflet, React-Leaflet, Leaflet-Draw |
| **Datos Geo** | TopoJSON, topojson-client |
| **Base de Datos** | SQLite (desarrollo) / PostgreSQL (producción) |

## 📁 Estructura del Proyecto

```
geovisor_costos/
├── backend/                 # Configuración Django
├── gestion_forestal/        # App principal Django
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas y API
│   ├── serializers.py       # Serializadores DRF
│   └── fixtures/            # Datos iniciales
├── frontend/                # Aplicación React
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── services/        # Servicios API
│   │   └── index.css        # Estilos globales
│   └── public/geo/          # Archivos TopoJSON
├── docs/                    # Documentación
└── requirements.txt         # Dependencias Python
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.10+
- Node.js 18+
- Git

### Backend (Django)

```bash
# Clonar el repositorio
git clone https://github.com/WGCUSP/geovisor_costos.git
cd geovisor_costos

# Crear y activar entorno virtual
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# o: venv\Scripts\activate     # Windows CMD
# o: source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Cargar datos iniciales (v1.0)
python manage.py seed_data
python manage.py import_distritos

# Ejecutar servidor
python manage.py runserver
```

### Frontend (React)

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev
```

### Acceso

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api/

## 📖 Documentación

La documentación completa se encuentra en la carpeta `docs/`:

| Documento | Descripción |
|-----------|-------------|
| [MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md) | Guía paso a paso para usuarios finales |
| [MANUAL_TECNICO.md](docs/MANUAL_TECNICO.md) | Arquitectura y detalles del sistema |
| [TASK_LIST.md](docs/TASK_LIST.md) | Lista de tareas por fase |
| [ROADMAP.md](docs/ROADMAP.md) | Roadmap de versiones |
| [FASES_DESARROLLO.md](docs/FASES_DESARROLLO.md) | Fases del proyecto |
| [REGLAS_DESARROLLO.md](docs/REGLAS_DESARROLLO.md) | Convenciones de código |
| [SDLC.md](docs/SDLC.md) | Ciclo de vida del desarrollo |
| [MEJORAS_FUTURAS.md](docs/MEJORAS_FUTURAS.md) | Backlog de mejoras |

## 🌳 Departamentos Soportados

El sistema incluye datos geográficos para 7 departamentos de Perú:

1. Ancash
2. San Martín
3. Cajamarca
4. Madre de Dios
5. Huánuco
6. Junín
7. Pasco

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**wigsdev**

---

*Desarrollado para el sector forestal del Perú 🇵🇪*
