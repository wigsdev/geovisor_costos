# Manual de Usuario - Geovisor Costos Forestales v1.1

## 1. Introducción
El Geovisor permite estimar costos de inversión para plantaciones forestales considerando variables geopaciales y técnicas específicas de cada región del Perú.

🔗 **Acceso a la Aplicación:** [https://geovisor-costos-web.up.railway.app/](https://geovisor-costos-web.up.railway.app/)

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
   - **Año Inicio / Fin:** Defina si desea calcular solo la instalación (0-0) o todo el flujo (0-20).
6. **Servicios Opcionales:**
   - Casilla "Incluir Servicios" (Gestión/Asistencia Técnica).
   - *Nota:* Se activa/desactiva automáticamente según el tamaño del área (>10 ha).

### Paso 3: Definir el Área
1. En el mapa, localice la herramienta de dibujo (polígono) en la esquina superior derecha.
2. Haga clic en los vértices del terreno a plantar.
3. Haga doble clic para cerrar el polígono.
> *El área en hectáreas se calculará automáticamente.*

### Paso 4: Cálculo y Reporte
1. Presione el botón verde **"Calcular Costos"**.
2. Revise el panel de resultados.
3. Use el botón **"📄 Exportar Reporte PDF"** para descargar un informe detallado.

## 3. Interpretación y Ajustes

- **Resumen:** Muestra Costo Total, Hectáreas, Densidad Real y Factores aplicados.
- **Botón ✏️ Editar:** Cierra los resultados pero **mantiene el polígono** y sus datos, permitiéndole modificar años o servicios antes de recalcular.
- **Botón 🗑️ Nuevo:** Borra todo (incluyendo el polígono) para iniciar un proyecto desde cero.

## 4. Preguntas Frecuentes

**¿Por qué no puedo dibujar?**
Debe seleccionar primero un Distrito y un Cultivo válido.

**¿Cómo borro el polígono?**
Use el icono de papelera en las herramientas del mapa y haga clic sobre el polígono.
