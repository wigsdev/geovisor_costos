# 📋 PROMPT MAESTRO Y DOCUMENTACIÓN TÉCNICA: MOTOR FORESTAL (CONSOLIDADO)

**Versión:** 2.1 (Consolidada)
**Rol:** Arquitecto de Software Senior / Ingeniero Agrónomo
**Alcance:** Backend (Lógica de Negocio), Base de Datos Referencial y Reglas de Entrada.

---

## 1. VISIÓN GENERAL DEL SISTEMA
El Geovisor no es una tabla estática de precios; es un **Modelo Paramétrico Dinámico**.
El sistema calcula el costo de inversión por hectárea basándose en:
1.  **Coeficientes Técnicos (Base de Datos):** Valores fijos y calibrados por especie/región (rendimiento MO, insumos).
2.  **Variables de Usuario (Frontend):** Distancias de siembra, precios de jornales y costo de plantones, validadas estrictamente.

### 1.1 Principios de Diseño
La aplicación debe ser **robusta**:
*   **Validación de Rango:** Rechazar distancias o precios fuera de la realidad técnica.
*   **Consistencia Matemática:** Los cálculos se derivan de fórmulas geométricas, no de valores pre-calculados.
*   **Trazabilidad:** Desglose claro de costos (Biológico, Laboral, Insumos, Gestión).

---

## 2. INTERFAZ DE ENTRADA (INPUTS)

El sistema recibe un objeto JSON con la configuración. Se combinan las definiciones de UI con las reglas de validación del backend.

| Variable | Tipo / UI | Restricción (Validación Backend) | Valor por Defecto (Fallback) |
| :--- | :--- | :--- | :--- |
| `region_id` | Select | Obligatorio | - |
| `especie_id` | Select | Obligatorio | - |
| `sistema` | Enum (Dropdown) | `[CUADRADO, RECTANGULO, TRES_BOLILLO]` | DB Default |
| `d_fila` | Float (Input) | **Min: 1.5m, Max: 10.0m** | DB Default |
| `d_planta` | Float (Input) | **Min: 1.5m, Max: 10.0m** | DB Default |
| `precio_jornal` | Currency (Input) | **Min: S/ 30.00** | DB Default |
| `precio_planton` | Currency (Input) | **Min: S/ 0.10** | DB Default |

---

## 3. LÓGICA DE NEGOCIO (CORE ALGORITHMS)

### 3.1. Motor de Densidad (Plantas/Ha)
Calcula el número de árboles basado en la geometría.
*Regla: Siempre redondear hacia arriba (`ceil`).*

*   **Rectangular / Cuadrado:**
    $$Density = \lceil \frac{10,000}{d\_fila \times d\_planta} \rceil$$

*   **Tres Bolillo (Triangular):**
    $$Density = \lceil \frac{10,000}{(d\_fila)^2 \times \sin(60^{\circ})} \rceil$$
    *Nota: Se usa $\sin(60^{\circ}) \approx 0.866$. Si $d\_fila \neq d\_planta$, usar $d\_fila$ como base.*

### 3.2. Motor de Esfuerzo Laboral (Ajuste Dinámico)
El costo de mano de obra no es lineal respecto a la densidad. Se usa un **Modelo 50/50**:

1.  **Recuperar Base:** Obtener `JORNALES_BASE` y `DENSIDAD_BASE` (calculada con las distancias default de la DB para esa especie).
2.  **Factor de Intensidad:**
    $$Factor = \frac{Densidad_{Usuario}}{Densidad_{Base}}$$
3.  **Fórmula de Ajuste:**
    *   **50% Fijo:** Logística, limpieza, trazo (no depende de la cantidad de árboles).
    *   **50% Variable:** Hoyación, plantación (depende directamente).
    $$Jornales_{Reales} = (Jornales_{Base} \times 0.5) + (Jornales_{Base} \times 0.5 \times Factor)$$
4.  **Redondeo:** $\lceil Jornales_{Reales} \rceil$

### 3.3. Cálculo Financiero (Inversión Año 0-1)
1.  **Costo Biológico:** $Densidad_{Usuario} \times Precio_{Planton}$
2.  **Costo Laboral:** $Jornales_{Reales} \times Precio_{Jornal}$
3.  **Insumos:** Valor fijo (`COSTO_INSUMOS`) recuperado de la DB.
4.  **Gastos Generales:** $Subtotal \times \%Gestion$ (de la DB).
5.  **Total:** Suma de todo lo anterior.

---

## 4. DATA SEED (Datos Maestros Normalizados V2)

Utilizar estrictamente estos datos recalibrados.

### TABLA 1: COEFICIENTES DE INSTALACIÓN (Parámetros Técnicos)

| ID | REGION | ESPECIE | SISTEMA | D_FILA | D_PLANTA | P_PLANTON | JORNALES_BASE | INSUMOS | GESTION |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | CAJAMARCA | Pino Radiata | TRES_BOLILLO | 3 | 3 | 0.8 | 60 | 1200 | 0.1 |
| 2 | CAJAMARCA | Pino Patula | TRES_BOLILLO | 3 | 3 | 0.8 | 60 | 1200 | 0.1 |
| 3 | CAJAMARCA | Eucalipto Globulus | CUADRADO | 3 | 3 | 0.8 | 55 | 1100 | 0.1 |
| 4 | ANCASH | Eucalipto Globulus | CUADRADO | 3 | 3 | 1.0 | 60 | 1200 | 0.1 |
| 5 | ANCASH | Pino Radiata | CUADRADO | 3 | 3 | 1.0 | 65 | 1300 | 0.1 |
| 6 | ANCASH | Tara (Caesalpinia) | RECTANGULO | 4 | 4 | 2.5 | 50 | 800 | 0.1 |
| 7 | PASCO | Pino Tecunumanii | RECTANGULO | 4 | 3 | 1.5 | 70 | 1400 | 0.12 |
| 8 | PASCO | Eucalipto Urograndis | RECTANGULO | 3 | 3 | 2.0 | 65 | 1500 | 0.12 |
| 9 | PASCO | Ulcumano (Nativa) | RECTANGULO | 4 | 4 | 3.0 | 75 | 1200 | 0.12 |
| 10 | JUNIN | Eucalipto Tropical | RECTANGULO | 3 | 2.5 | 2.5 | 70 | 1800 | 0.12 |
| 11 | JUNIN | Pino Tecunumanii | RECTANGULO | 3 | 3 | 1.8 | 75 | 1600 | 0.12 |
| 12 | JUNIN | Bolaina Blanca | CUADRADO | 3 | 3 | 1.5 | 80 | 1500 | 0.12 |
| 13 | HUANUCO | Bolaina Blanca | CUADRADO | 3 | 3 | 1.5 | 85 | 1400 | 0.12 |
| 14 | HUANUCO | Capirona | RECTANGULO | 4 | 3 | 1.8 | 85 | 1400 | 0.12 |
| 15 | SAN MARTIN | Teca (Clonal) | CUADRADO | 3 | 4 | 3.5 | 80 | 1800 | 0.15 |
| 16 | SAN MARTIN | Capirona | RECTANGULO | 4 | 3 | 1.5 | 80 | 1500 | 0.15 |
| 17 | SAN MARTIN | Eucalipto Urograndis | CUADRADO | 3 | 3 | 2.5 | 75 | 1800 | 0.15 |
| 18 | MADRE DE DIOS | Shihuahuaco | RECTANGULO | 4 | 4 | 5.0 | 85 | 2000 | 0.15 |
| 19 | MADRE DE DIOS | Teca | RECTANGULO | 4 | 4 | 4.0 | 80 | 2000 | 0.15 |
| 20 | MADRE DE DIOS | Castaña (Injerto) | RECTANGULO | 7 | 7 | 15.0 | 60 | 1500 | 0.15 |

### TABLA 2: PARÁMETROS DE MANTENIMIENTO (Años 2+)

| REGION | NIVEL_MALEZA | LIMPIEZA (Días) | PODAS (Días) | TOTAL DÍAS | INSUMOS (S/) | JORNAL REF (S/) |
|:---|:---|:---|:---|:---|:---|:---|
| CAJAMARCA | BAJO | 15 | 5 | 20 | 200 | 40 |
| ANCASH | BAJO | 17 | 5 | 22 | 200 | 40 |
| PASCO | MEDIO | 20 | 6 | 26 | 300 | 45 |
| JUNIN | MEDIO | 22 | 6 | 28 | 400 | 50 |
| HUANUCO | ALTO | 25 | 7 | 32 | 300 | 50 |
| SAN MARTIN | ALTO | 25 | 8 | 33 | 500 | 55 |
| MADRE DE DIOS | MEDIO | 20 | 5 | 25 | 400 | 60 |

---

## 5. TEST DE VALIDACIÓN (GOLDEN PATH)

El sistema **DEBE** replicar este resultado exacto para ser considerado correcto.

**Escenario:** SAN MARTIN - TECA - TRES BOLILLO - 3.5m (distancia).

1.  **Input:** Distancia 3.5m, Precio Jornal Default (55), Precio Planton Default (3.50).
2.  **Densidad Esperada:** $10000 / (3.5^2 \times 0.866) \approx 943$ plantas.
3.  **Factor Ajuste:**
    *   Base DB (Id 15): $3 \times 4 = 12m^2 \rightarrow 833$ plantas. Jornales Base: 80.
    *   Ratio: $943 / 833 = 1.132$.
4.  **Jornales Reales:**
    *   Fijos: 40.
    *   Variables: $40 \times 1.132 = 45.28$.
    *   Total: $85.28 \rightarrow$ **86 días**.
5.  **Costos:**
    *   Plantones: $943 \times 3.50 = 3300.50$
    *   Mano Obra: $86 \times 55.00 = 4730.00$
    *   Insumos: $1800.00$
    *   Subtotal: $9830.50$
    *   **TOTAL (x 1.15): S/ 11,305.08**
