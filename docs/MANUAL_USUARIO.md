# Manual de Usuario - Geovisor Costos Forestales v1.1

## 1. Introducción
El Geovisor permite estimar costos de inversión para plantaciones forestales considerando variables geopaciales y técnicas específicas de cada región del Perú.

## 2. Flujo de Trabajo

### Paso 1: Ubicación
En el panel lateral izquierdo:
1. Seleccione el **Departamento**.
2. Seleccione la **Provincia**.
3. Seleccione el **Distrito**.
> *El sistema hará zoom automático en el mapa mostrando los límites administrativos.*

### Paso 2: Configuración del Cultivo
1. **Especie Forestal:** Elija entre las especies disponibles para la zona seleccionada.
2. **Sistema de Siembra:**
   - *Cuadrado* (ej. 3x3)
   - *Rectangular* (ej. 4x3)
   - *Tres Bolillo* (Triangular)
3. **Distanciamientos:** Ingrese la distancia entre filas y plantas (en metros).
4. **Validación de Costos:**
   - El sistema carga precios sugeridos para **Jornal** y **Plantón**.
   - Puede modificar estos valores si tiene precios locales más precisos.
5. **Rango de Presupuesto:**
   - **Año Inicio / Fin:** Defina si desea calcular solo la instalación (0-0) o todo el flujo (0-20).

### Paso 3: Definir el Área
1. En el mapa, localice la herramienta de dibujo (polígono) en la esquina superior derecha.
2. Haga clic en los vértices del terreno a plantar.
3. Haga doble clic para cerrar el polígono.
> *El área en hectáreas se calculará automáticamente.*

### Paso 4: Cálculo
1. Presione el botón verde **"Calcular Costos"**.
2. Revise el panel de resultados que aparecerá sobre el mapa.

## 3. Interpretación de Resultados

- **Resumen:** Muestra Costo Total, Hectáreas, Densidad Real y Factores aplicados.
- **Tabla Anual:** Desglose año a año de Mano de Obra, Insumos y Servicios.
- **Botón Limpiar:** Cierra los resultados y permite reajustar parámetros (el polígono se mantiene para facilitar recálculos).

## 4. Preguntas Frecuentes

**¿Por qué no puedo dibujar?**
Debe seleccionar primero un Distrito y un Cultivo válido.

**¿Cómo borro el polígono?**
Use el icono de papelera en las herramientas del mapa y haga clic sobre el polígono.
