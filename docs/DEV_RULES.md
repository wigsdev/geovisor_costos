# REGLAS DE DESARROLLO Y ESTÁNDARES DEL PROYECTO (GEOVISOR)

## 1. Filosofía del Código
* **Clean Code:** El código debe ser legible por humanos. Variables descriptivas (ej: `costo_total_hectarea` en lugar de `c`).
* **KISS (Keep It Simple, Stupid):** Soluciones simples sobre complejas.
* **DRY (Don't Repeat Yourself):** Si copias y pegas código, crea una función.
* **Typing:** Todo el código Python debe tener "Type Hints" (ej: `def calcular(area: float) -> float:`).

## 2. Control de Versiones (Git Flow & Commits)
Seguiremos el estándar **Conventional Commits**. Cada commit debe tener esta estructura:

* `feat: descripción` (Para nuevas funcionalidades)
* `fix: descripción` (Para corrección de errores)
* `docs: descripción` (Para cambios en documentación)
* `style: descripción` (Cambios de formato, espacios, etc.)
* `refactor: descripción` (Mejoras de código sin cambiar funcionalidad)
* `chore: descripción` (Mantenimiento, configuración de entorno)

**Ejemplo correcto:** `feat: agregar modelo de costos para Bolaina`
**Ejemplo incorrecto:** `agregando cosas`

## 3. Documentación (Docstrings)
* **Python:** Toda función y clase debe tener Docstrings formato Google/NumPy.
    ```python
    def calcular_costo(area: float) -> float:
        """
        Calcula el costo total basado en el área.
        
        Args:
            area (float): Cantidad de hectáreas.
            
        Returns:
            float: Costo total en Soles.
        """
    ```
* **JavaScript:** Usar JSDoc para componentes complejos.

## 4. Estructura y Seguridad
* **Secretos:** NUNCA subir contraseñas o API Keys al repositorio. Usar siempre variables de entorno (`.env`).
* **Idioma:**
    * Código (Variables/Funciones): Español (para coincidir con el dominio del negocio agronómico local) o Inglés (Estándar). *Decisión: Variables en Español Descriptivo*.
    * Comentarios/Commits: Español.

## 5. Flujo de Trabajo con el Agente
1. Leer requerimiento.
2. Planear la solución (explicar qué se va a hacer).
3. Escribir/Modificar código.
4. Sugerir el mensaje de Commit apropiado.