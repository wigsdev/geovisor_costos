# Reglas de Desarrollo - Geovisor Costos Forestales

## 1. Estructura del Proyecto

```
geovisor_costos/
├── backend/                 # Configuración Django
├── gestion_forestal/        # App principal Django
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas y API endpoints
│   ├── serializers.py       # Serializadores DRF
│   └── urls.py              # Rutas de la API
├── frontend/                # Aplicación React
│   ├── src/
│   │   ├── components/      # Componentes React
│   │   ├── services/        # Servicios API
│   │   └── index.css        # Estilos globales
│   └── public/
│       └── geo/             # Archivos TopoJSON
├── docs/                    # Documentación
└── venv/                    # Entorno virtual Python
```

---

## 2. Convenciones de Código

### Python (Backend)
- PEP 8 para estilo de código
- Docstrings en funciones públicas
- Type hints donde sea posible
- Tests unitarios para lógica de negocio

### JavaScript/React (Frontend)
- ES6+ syntax
- Componentes funcionales con hooks
- Props destructuring
- Nombres descriptivos en español para etiquetas UI

### CSS
- CSS puro (sin Tailwind v4)
- Clases utilitarias manuales
- Variables CSS para colores del tema
- Mobile-first responsive design

---

## 3. Git Workflow

### Branches
- `main` - Producción
- `develop` - Desarrollo activo
- `feature/*` - Nuevas funcionalidades
- `fix/*` - Correcciones de bugs

### Commits
Usar Conventional Commits:
- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Documentación
- `style:` Formato/estilos
- `refactor:` Refactorización
- `test:` Tests

Ejemplo:
```
feat(frontend): add TopoJSON layers with auto-zoom
fix(css): improve Leaflet Draw icons visibility
docs: create project documentation structure
```

---

## 4. API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/distritos/` | Lista de distritos |
| GET | `/api/cultivos/` | Lista de cultivos |
| POST | `/api/calcular-costos/` | Calcular costos |

---

## 5. Colores del Tema

| Variable | Color | Uso |
|----------|-------|-----|
| Primary | `#10b981` | Acciones principales, éxito |
| Background | `#0f172a` | Fondo principal |
| Surface | `#1e293b` | Tarjetas, paneles |
| Border | `#334155` | Bordes sutiles |
| Text Primary | `#ffffff` | Texto principal |
| Text Secondary | `#94a3b8` | Texto secundario |

---

## 6. Comandos Útiles

### Backend
```bash
# Activar entorno virtual
source venv/Scripts/activate

# Iniciar servidor
python manage.py runserver

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Cargar fixtures
python manage.py loaddata initial_data.json
```

### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build producción
npm run build
```

---

## 7. Testing

### Backend
```bash
python manage.py test
```

### Frontend
```bash
npm run test
```

---

## 8. Checklist Pre-Commit

- [ ] Código formateado
- [ ] Sin errores de consola
- [ ] Probado en navegador
- [ ] Documentación actualizada si aplica
- [ ] Mensaje de commit descriptivo
