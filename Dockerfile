# Usar Python 3.10 slim como base (ligera y eficiente)
FROM python:3.10-slim

# Evitar que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE 1
# Evitar buffer en la salida estándar para ver logs en tiempo real
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# ==================================================
# INSTALACIÓN DE DEPENDENCIAS DEL SISTEMA (GEODJANGO)
# ==================================================
# Actualizar lista de paquetes e instalar dependencias esenciales
# binutils, libproj-dev, gdal-bin: Requeridos para GeoDjango
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ==================================================
# INSTALACIÓN DE DEPENDENCIAS DE PYTHON
# ==================================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==================================================
# CÓDIGO FUENTE Y ARCHIVOS
# ==================================================
COPY . .

# Recolectar archivos estáticos para WhiteNoise
RUN python manage.py collectstatic --noinput

# ==================================================
# COMANDO DE INICIO (PRODUCCIÓN)
# ==================================================
# Usar Gunicorn como servidor WSGI
# $PORT es inyectado por Railway automáticamente
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
