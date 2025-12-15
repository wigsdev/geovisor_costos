PROMPT: CONFIGURACIÓN DE GEODJANGO + POSTGIS PARA PRODUCCIÓN 🌍

ROL: DevOps Engineer & Django Backend Specialist.

CONTEXTO:

Vamos a desplegar el backend en Railway.

Actualmente usamos SQLite, pero para producción necesitamos PostgreSQL con la extensión PostGIS.

Además, GeoDjango requiere librerías de sistema C++ (GDAL, GEOS) que no vienen en los entornos Python estándar.

OBJETIVO:

Preparar el repositorio para un despliegue exitoso en Railway con soporte espacial completo.

INSTRUCCIONES TÉCNICAS:

1. Actualización de Dependencias (requirements.txt):

Agrega las siguientes librerías esenciales para producción:



psycopg2-binary (Adaptador de base de datos PostgreSQL).

gunicorn (Servidor de aplicaciones WSGI para producción).

dj-database-url (Para leer la configuración de la BD desde variables de entorno).

whitenoise (Para servir archivos estáticos en producción).

2. Configuración del Proyecto (settings.py):

Modifica la configuración de DATABASES para que sea dinámica:



Si existe la variable de entorno DATABASE_URL (Producción), usa dj_database_url.config() y cambia el motor a 'django.contrib.gis.db.backends.postgis'.

Si no existe (Local), mantén SQLite (o tu configuración local).

Configura whitenoise en MIDDLEWARE para los archivos estáticos.

3. Creación del Dockerfile (CRÍTICO PARA GEODJANGO):

Crea un archivo llamado Dockerfile en la raíz del proyecto para definir el entorno exacto de Linux que Railway usará. Debe contener:



Base Image: python:3.10-slim (o la versión que uses).

System Dependencies: Ejecuta apt-get update e instala:

binutils

libproj-dev

gdal-bin

libgdal-dev

python3-gdal

Python Dependencies: Copia requirements.txt e instálalos.

Comando de Inicio: CMD gunicorn nombre_de_tu_proyecto.wsgi:application --bind 0.0.0.0:$PORT

ENTREGABLE:



El contenido actualizado de requirements.txt.

El bloque de código a modificar en settings.py.

El código completo del nuevo Dockerfile.