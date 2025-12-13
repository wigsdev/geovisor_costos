# PROMPT MAESTRO: GEOVISOR DE COSTOS FORESTALES (PERÚ) - VERSIÓN 2.0

## 1. Contexto del Proyecto
Estamos desarrollando un **Geovisor Web** para calcular costos de inversión y flujos de caja en plantaciones forestales comerciales en Perú.
El sistema utiliza una estrategia de **"Smart Defaults" (Valores por Defecto Inteligentes)**: la base de datos sugiere costos promedio por zona, pero el usuario final tiene el control para editarlos antes del cálculo.

**Objetivo:** Permitir a inversores estimar costos para especies clave (Bolaina, Pino, Eucalipto, Capirona), ajustando variables críticas como mano de obra y dificultad del terreno sin depender inicialmente de geometrías complejas.

## 2. Stack Tecnológico (Estricto)
* **Backend:** Python 3.10+
* **Framework:** Django 4.2+ & Django REST Framework (DRF).
* **Base de Datos:** PostgreSQL 14+.
* **Frontend:** React + Vite + Tailwind CSS.
* **Nota Técnica Fase 1:** Para agilizar el desarrollo y evitar conflictos de configuración en Windows, **NO usaremos `django.contrib.gis` (GDAL/GeometryField) en esta etapa**. Usaremos campos `DecimalField` para coordenadas y atributos lógicos para la topografía.

## 3. Arquitectura de Datos (Esquema de Base de Datos)

El agente debe implementar/refactorizar los siguientes modelos en `gestion_forestal/models.py`.

### A. Modelos Geográficos y Económicos
**Modelo: `ZonaEconomica`**
* Agrupa distritos con costos similares (Ej: "Selva Alta", "Sierra Rural").
* `nombre`: String.
* `costo_jornal_referencial`: Decimal (Valor sugerido para el frontend).
* `costo_planton_referencial`: Decimal (Valor sugerido para el frontend).

**Modelo: `Distrito`**
* Unidad administrativa mínima.
* `cod_ubigeo`: String (PK) - Código oficial INEI.
* `nombre`: String.
* `zona_economica`: ForeignKey -> `ZonaEconomica`. (Vital para sugerir precios).
* `latitud`: Decimal (Para marcador visual en mapa).
* `longitud`: Decimal.
* `pendiente_promedio_estimada`: Integer (Default 15). *Campo crítico para simular el análisis topográfico.*

### B. Modelos de Negocio
**Modelo: `Cultivo`**
* Catálogo de especies.
* `nombre`: String (Ej: "Bolaina Blanca", "Pino Patula").
* `turno_estimado`: Integer (Años hasta la cosecha).
* `densidad_base`: Integer (Árboles por hectárea, ej. 1111).

**Modelo: `PaqueteTecnologico` (La tabla más importante)**
* Define la "receta" de actividades por año.
* `cultivo`: FK -> `Cultivo`.
* `anio_proyecto`: Integer (0, 1, 2... donde 0 es instalación).
* `rubro`: ChoiceField ('MANO_OBRA', 'INSUMO', 'SERVICIOS', 'LEGAL', 'ACTIVO').
* `actividad`: String (Ej: "Hoyado 30x30", "Fertilizante NPK").
* `unidad_medida`: String ('Jornal', 'Kg', 'Unidad', 'Global').
* `cantidad_tecnica`: Decimal (Cantidad requerida por hectárea en terreno plano).
* `sensible_pendiente`: Boolean (True si la pendiente afecta el rendimiento, ej: Hoyado).
* `costo_unitario_referencial`: Decimal (Para insumos varios que NO son plantones).

## 4. Lógica de Negocio (Algoritmos a Implementar)

El agente debe crear un endpoint `/api/calcular-costos/` (POST).

* **Input del Request (Lo que envía el usuario):**
    * `distrito_id`, `cultivo_id`, `hectareas`.
    * `costo_jornal_usuario`: Decimal (El usuario valida o corrige el sugerido).
    * `costo_planton_usuario`: Decimal (El usuario valida o corrige el sugerido).
    * `anio_inicio` (default 0), `anio_fin`.

* **Lógica de Cálculo (Algoritmo):**
    1.  **Obtener Distrito:** Consultar la `pendiente_promedio_estimada` del distrito.
    2.  **Calcular Factor Pendiente:**
        * < 15% = 1.0 (Plano)
        * 15% - 30% = 1.15 (Ondulado)
        * > 30% = 1.30 (Ladera fuerte)
    3.  **Iterar Actividades:** Filtrar `PaqueteTecnologico` por cultivo y rango de años.
    4.  **Aplicar Fórmula por Actividad:**
        * Si `rubro` == 'MANO_OBRA':
            * `Costo = (Cantidad * Factor_Pendiente) * costo_jornal_usuario`. 
            * *(Solo aplicar factor pendiente si `sensible_pendiente` es True)*.
        * Si `rubro` == 'INSUMO' (Plantones):
             * `Costo = Cantidad * costo_planton_usuario`.
        * Si `rubro` == 'INSUMO' (Otros) o 'SERVICIOS':
             * `Costo = Cantidad * costo_unitario_referencial` (Dato fijo de la BD).
    5.  **Sumar Totales:** Agrupar por Rubro y por Año.

## 5. Instrucciones Paso a Paso para el Agente

**Fase 1: Refactorización Backend (Models)**
1.  Edita `models.py` para eliminar dependencias de `django.contrib.gis` y ajustar los campos según la Sección 3.
2.  Ejecuta `makemigrations` y `migrate`.

**Fase 2: API & Carga de Datos (Views)**
1.  Crea `serializers.py` (Incluyendo `DistritoSerializer` con los datos referenciales de la zona).
2.  Crea `views.py` implementando estrictamente la lógica de la Sección 4.
3.  Crea un script `management/commands/seed_data.py` para poblar con datos de prueba (1 Zona, 1 Distrito, 1 Cultivo, 3 Actividades) y verificar el funcionamiento.

**Fase 3: Frontend Inicial**
1.  Inicializa proyecto React con Vite.
2.  Instala `leaflet`, `react-leaflet`, `axios`.
3.  Crea la interfaz (Sidebar) que permita al usuario ver los precios sugeridos y editarlos antes de enviar a calcular.