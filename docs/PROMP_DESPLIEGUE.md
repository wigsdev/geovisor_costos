PROMPT: CONFIGURACIÓN DE GEODJANGO + POSTGIS PARA PRODUCCIÓN 🌍 (V2.0)

ROL: DevOps Engineer & Django Backend Specialist.

CONTEXTO:

Vamos a desplegar el backend en Railway.
Actualmente usamos SQLite, pero para producción necesitamos PostgreSQL con la extensión PostGIS y datos geográficos pre-cargados.

OBJETIVO:

Preparar el repositorio para un despliegue exitoso en Railway con soporte espacial completo y datos iniciales.

INSTRUCCIONES TÉCNICAS:

1. Actualización de Dependencias (requirements.txt):
   - psycopg2-binary
   - gunicorn
   - dj-database-url
   - whitenoise

2. Configuración del Proyecto (settings.py):
   - DB Dinámica (DATABASE_URL para PostGIS, SQLite local).
   - WhiteNoise para estáticos.

3. Dockerfile (GeoDjango):
   - Base: python:3.10-slim
   - Deps Sistema: binutils, libproj-dev, gdal-bin, libgdal-dev
   - Start Command: gunicorn ...

4. GESTIÓN DE DATOS (NUEVO REQUISITO):
   
   Es crítico poblar la base de datos al desplegar.
   
   A) Archivos Requeridos:
      El archivo `gestion_forestal/fixtures/UBIGEO_DISTRITOS.csv` DEBE estar en el repositorio.
      (Railway lo necesita para importar los 1800+ distritos).

   B) Comandos de Inicialización (Railway Shell):
      Una vez desplegado, ejecutar en orden:
      
      1. `python manage.py migrate` (Crear tablas)
      2. `python manage.py seed_data` (Cultivos, costos y 1 distrito prueba)
      3. `python manage.py import_distritos` (Carga masiva de distritos desde el CSV)
      4. `python manage.py createsuperuser` (Acceso admin)

ENTREGABLES:
- requirements.txt actualizado
- settings.py configurado
- Dockerfile validado
- CSV de distritos en `gestion_forestal/fixtures/`