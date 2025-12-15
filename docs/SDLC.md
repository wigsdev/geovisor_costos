# Ciclo de Vida del Desarrollo de Software (SDLC)

## Introducción

El **Ciclo de Vida del Desarrollo de Software** (SDLC por sus siglas en inglés: Software Development Life Cycle) es un proceso estructurado y sistemático utilizado para desarrollar software de alta calidad. Este marco proporciona una serie de fases que guían el desarrollo desde la concepción inicial hasta el mantenimiento continuo del producto.

---

## Fases del SDLC

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. PLANIFI- │───►│ 2. ANÁLISIS │───►│  3. DISEÑO  │───►│ 4. DESARRO- │
│    CACIÓN   │    │             │    │             │    │     LLO     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │
│ 7. MANTENI- │◄───│ 6. IMPLEMEN-│◄───│  5. PRUEBAS │◄──────────┘
│    MIENTO   │    │    TACIÓN   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 1. Planificación

### Objetivo
Definir el alcance, objetivos y viabilidad del proyecto.

### Actividades
- Identificar necesidades del negocio
- Definir objetivos del proyecto
- Estimar recursos (tiempo, presupuesto, personal)
- Evaluar riesgos
- Crear cronograma inicial

### Entregables
| Documento | Descripción |
|-----------|-------------|
| Acta de constitución | Define formalmente el proyecto |
| Plan de proyecto | Cronograma, recursos, hitos |
| Análisis de viabilidad | Técnica, económica, operacional |

### Preguntas Clave
- ¿Es factible el proyecto?
- ¿Cuáles son los objetivos principales?
- ¿Qué recursos se necesitan?
- ¿Cuál es el cronograma estimado?

---

## 2. Análisis de Requisitos

### Objetivo
Comprender y documentar las necesidades del usuario y del sistema.

### Actividades
- Recopilar requisitos con stakeholders
- Analizar requisitos funcionales y no funcionales
- Documentar casos de uso
- Priorizar requisitos
- Validar con usuarios

### Entregables
| Documento | Descripción |
|-----------|-------------|
| SRS (Especificación de Requisitos) | Requisitos funcionales y no funcionales |
| Casos de uso | Escenarios de interacción |
| Historias de usuario | Requisitos desde perspectiva del usuario |

### Preguntas Clave
- ¿Qué debe hacer el sistema?
- ¿Quiénes son los usuarios?
- ¿Cuáles son las restricciones?
- ¿Cómo se medirá el éxito?

---

## 3. Diseño

### Objetivo
Definir la arquitectura y estructura técnica del sistema.

### Actividades
- Diseñar arquitectura del sistema
- Definir modelos de datos
- Crear prototipos de interfaz
- Seleccionar tecnologías
- Documentar especificaciones técnicas

### Entregables
| Documento | Descripción |
|-----------|-------------|
| Documento de diseño | Arquitectura, componentes, APIs |
| Modelo de datos | Esquema de base de datos |
| Mockups/Wireframes | Diseño de interfaces |
| Diagrama de arquitectura | Estructura del sistema |

### Tipos de Diseño

```
┌────────────────────────────────────────────────────────┐
│                   DISEÑO DE ALTO NIVEL                 │
│   Arquitectura general, módulos, integración externa   │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                  DISEÑO DE BAJO NIVEL                  │
│   Componentes internos, clases, funciones, algoritmos  │
└────────────────────────────────────────────────────────┘
```

---

## 4. Desarrollo (Codificación)

### Objetivo
Construir el software según las especificaciones de diseño.

### Actividades
- Escribir código fuente
- Implementar funcionalidades
- Realizar revisiones de código
- Documentar código
- Control de versiones

### Entregables
| Entregable | Descripción |
|------------|-------------|
| Código fuente | Implementación funcional |
| Documentación técnica | Comentarios, APIs documentadas |
| Base de datos | Esquema implementado |
| Scripts de build | Automatización de compilación |

### Buenas Prácticas
- Seguir estándares de codificación
- Escribir código limpio y mantenible
- Usar control de versiones (Git)
- Realizar commits frecuentes
- Documentar decisiones técnicas

---

## 5. Pruebas (Testing)

### Objetivo
Verificar que el software funciona correctamente y cumple los requisitos.

### Tipos de Pruebas

| Tipo | Alcance | Responsable |
|------|---------|-------------|
| Unitarias | Funciones individuales | Desarrolladores |
| Integración | Módulos conectados | QA/Desarrolladores |
| Sistema | Sistema completo | QA |
| Aceptación | Requisitos del usuario | Usuario/Cliente |
| Rendimiento | Velocidad, carga | QA |
| Seguridad | Vulnerabilidades | Especialistas |

### Actividades
- Crear casos de prueba
- Ejecutar pruebas
- Reportar defectos
- Verificar correcciones
- Pruebas de regresión

### Entregables
| Documento | Descripción |
|-----------|-------------|
| Plan de pruebas | Estrategia y cronograma |
| Casos de prueba | Escenarios detallados |
| Reporte de bugs | Defectos encontrados |
| Informe de pruebas | Resultados y cobertura |

---

## 6. Implementación (Despliegue)

### Objetivo
Poner el software en producción para uso de los usuarios finales.

### Actividades
- Preparar ambiente de producción
- Migrar datos (si aplica)
- Desplegar aplicación
- Configurar monitoreo
- Capacitar usuarios

### Estrategias de Despliegue

| Estrategia | Descripción | Riesgo |
|------------|-------------|--------|
| Big Bang | Todo de una vez | Alto |
| Por fases | Funcionalidades graduales | Medio |
| Paralelo | Sistemas viejo y nuevo simultáneos | Bajo |
| Blue-Green | Dos ambientes intercambiables | Bajo |
| Canary | Subconjunto de usuarios primero | Bajo |

### Entregables
| Entregable | Descripción |
|------------|-------------|
| Sistema en producción | Software funcionando |
| Documentación de usuario | Manuales, guías |
| Plan de rollback | Procedimiento de reversión |
| Checklist de despliegue | Verificaciones pre/post |

---

## 7. Mantenimiento

### Objetivo
Asegurar el funcionamiento continuo y evolución del software.

### Tipos de Mantenimiento

| Tipo | Propósito | Ejemplo |
|------|-----------|---------|
| Correctivo | Corregir defectos | Bug fixes |
| Adaptativo | Adaptar a cambios externos | Nueva versión de OS |
| Perfectivo | Mejorar funcionalidad | Nuevas características |
| Preventivo | Prevenir problemas futuros | Refactorización |

### Actividades
- Monitorear rendimiento
- Atender incidentes
- Aplicar parches de seguridad
- Implementar mejoras
- Actualizar documentación

### Entregables
| Entregable | Descripción |
|------------|-------------|
| Releases de actualización | Versiones con correcciones/mejoras |
| Registros de cambios | Changelog |
| Métricas de sistema | Disponibilidad, rendimiento |
| Tickets resueltos | Historial de soporte |

---

## Modelos de SDLC

### Modelo en Cascada (Waterfall)
```
Planif. ─► Análisis ─► Diseño ─► Desarrollo ─► Pruebas ─► Despliegue
```
- Secuencial, sin retorno
- Adecuado para proyectos bien definidos

### Modelo Iterativo
```
    ┌─────────────────────────────────┐
    │  Planif. ─► Diseño ─► Código ─► │
    │  Pruebas ─────────────┐         │
    │        ▲              │         │
    │        └──────────────┘         │
    └─────────────────────────────────┘
```
- Ciclos repetitivos de desarrollo
- Permite refinamiento continuo

### Modelo Ágil (Agile)
```
Sprint 1      Sprint 2      Sprint 3
┌────────┐   ┌────────┐   ┌────────┐
│Plan    │   │Plan    │   │Plan    │
│Design  │   │Design  │   │Design  │
│Code    │   │Code    │   │Code    │
│Test    │   │Test    │   │Test    │
│Release │   │Release │   │Release │
└────────┘   └────────┘   └────────┘
   2-4 sem      2-4 sem      2-4 sem
```
- Entregas incrementales
- Adaptación al cambio
- Colaboración continua

---

## Aplicación en Geovisor Costos Forestales

| Fase SDLC | Aplicación en el Proyecto |
|-----------|---------------------------|
| Planificación | Definir alcance: visor de costos forestales para Perú |
| Análisis | Identificar usuarios, requisitos de cálculo, datos geográficos |
| Diseño | Arquitectura Django+React, modelo de datos, UI/UX |
| Desarrollo | Implementar backend, frontend, integración de mapas |
| Pruebas | Validar cálculos, probar interfaces, pruebas de usabilidad |
| Implementación | Desplegar en servidor, configurar dominio |
| Mantenimiento | Actualizaciones, nuevas especies, correcciones |

---

## Referencias

- IEEE 12207 - Procesos del ciclo de vida del software
- ISO/IEC 15288 - Ingeniería de sistemas
- PMBOK - Project Management Body of Knowledge
- Agile Manifesto - Principios de desarrollo ágil
