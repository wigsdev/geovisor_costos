# Guía de Despliegue - Geovisor v1.1

## 1. Requisitos Previos
- Cuenta en Railway (o proveedor similar).
- Docker instalado (para pruebas locales).
- Repositorio Git con el código fuente.

## 2. Variables de Entorno
Configurar las siguientes variables en producción:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DEBUG` | Modo debug Django | `False` |
| `SECRET_KEY` | Llave secreta Django | `django-insecure-...` |
| `DATABASE_URL` | URL de conexión PostgreSQL | `postgresql://user:pass@host:port/db` |
| `ALLOWED_HOSTS` | Dominios permitidos | `geovisorcostos-production.up.railway.app` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes confiables | `https://geovisor-costos-web.up.railway.app` |
| `VITE_API_URL` | URL del API Backend (Frontend) | `https://geovisorcostos-production.up.railway.app/api` |

## 3. Despliegue en Railway

### 3.1 Servicio Backend
1. **Nuevo Servicio** -> Desde Repo GitHub.
2. **Directorios:**
   - Root Directory: `/`
3. **Build Command:** (Automático por Dockerfile)
4. **Start Command:** (Definido en Dockerfile)
   ```bash
   /bin/sh -c "python manage.py migrate && python manage.py seed_data_v1_1 && python manage.py import_distritos && gunicorn --workers 1 --bind 0.0.0.0:$PORT backend.wsgi:application"
   ```
   > *Nota: Usar 1 worker en planes gratuitos para evitar OOM.*

### 3.2 Servicio Frontend
1. **Nuevo Servicio** -> Desde Repo GitHub.
2. **Directorios:**
   - Root Directory: `/frontend`
3. **Build Command:** `npm run build`
4. **Start Command:** `nginx -g "daemon off;"` (Usa Dockerfile propio del frontend)

## 4. Configuración Docker

El proyecto usa un **Dockerfile multi-stage** en la raíz para el backend y uno en `/frontend` para la web.

### Backend Dockerfile
- Base: `python:3.13.1-slim`
- Dependencias Sistema: `gdal-bin`, `libgdal-dev` (Crítico para GeoDjango)
- Instala requirements y copia el código.

### Frontend Dockerfile
- Stage 1 (Build): `node:20` -> `npm run build`
- Stage 2 (Serve): `nginx:alpine` -> Copia build a `/usr/share/nginx/html`

## 5. Mantenimiento Post-Despliegue

### Actualización de Datos
Para recargar la data maestra en producción, ejecutar en la consola del servicio:
```bash
python manage.py seed_data_v1_1
```
