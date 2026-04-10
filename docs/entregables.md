# Entregables - Deteccion de Fraude
**Especializacion en IA | Modulo 4 | Pontificia Universidad Javeriana**
**Metodologia:** CRISP-DM
**Dataset:** PaySim — Synthetic Financial Datasets For Fraud Detection (Kaggle)
**Fuente de contexto:** https://www.portal.euromonitor.com/magazine/homemain

---

## PUNTO 1 — Entendimiento del Negocio

> El taller exige: contexto del caso, marco legal, entidad financiera con elementos financieros/tecnicos/operacionales, etica. **Toda la informacion debe estar citada de fuentes confiables y relevantes.**

### 1.1 Contexto del caso — Deteccion de Fraude
- [x] Descripcion del problema de fraude financiero
- [x] Contexto con datos de mercado citados (Euromonitor 2024-2025: perdidas >$33.5B USD, m-commerce +250%)

### 1.2 Marco legal — obligatorio por el taller
- [x] **Art. 246 Codigo Penal** — Estafa: como afecta al usuario
- [x] **Art. 316 Codigo Penal** — Captacion masiva de dineros
- [x] **Art. 323 Codigo Penal** — Lavado de activos + SARLAFT
- [x] **Art. 327 Codigo Penal** — Enriquecimiento ilicito
- [x] **Art. 2341 Codigo Civil** — Responsabilidad extracontractual: banco debe restituir fondos por FN
- [x] **Art. 15 Constitucion Politica** — Habeas Data: FP vulnera derechos del cliente
- [x] Otros relevantes: Ley 1266/2008, Ley 1328/2009, Circular SFC 29/2014, Sentencia T-255/22
- [x] Como afecta al usuario cada norma (descrito por articulo)
- [x] Debido proceso de la organizacion ante un caso de fraude (3 dimensiones: tecnica, operacional, legal)

### 1.3 Entidad financiera: Banco Falabella
- [x] Elementos **financieros**: perfil, tarjeta CMR, segmento retail, cartera
- [x] Elementos **tecnicos**: app, web, Visa/Mastercard, procesamiento en tiempo real
- [x] Elementos **operacionales**: SARLAFT, canales digitales, protocolo bloqueo/reactivacion
- [ ] **PENDIENTE:** citas especificas con fuentes verificables (reporte anual Grupo Falabella, SFC, noticias sectoriales)

### 1.4 Etica en la toma de decisiones
- [x] Como la toma de decisiones automatizada implica un tema etico
- [x] FAccT framework (Fairness, Accountability, Transparency)
- [x] Sesgo algoritmico: thin-file, discriminacion demografica
- [x] Problema de la caja negra: RF y CatBoost opacos ante juez de tutela
- [x] Solucion XAI: SHAP y LIME citados con fuente

---

## PUNTO 2 — Entendimiento de los Datos

> El taller exige: tamano, faltantes/tipos, estadistica descriptiva con interpretacion, histogramas/correlacion/boxplots. Aplicar sobre el dataset **original sin balancear**.

### 2a. Tamano de la base de datos
- [x] Numero de filas y columnas (6.362.620 x 11)
- [x] Descripcion de cada variable (diccionario completo)

### 2b. Datos faltantes y tipo de variables
- [x] Tipos de variables (`df.info()` ejecutado)
- [x] Valores faltantes (cubiertos por ydata_profiling — reporte HTML)
- [ ] Valores unicos por variable categorica *(pendiente — celda dedicada)*
- [ ] Duplicados *(pendiente — celda dedicada)*

### 2c. Analisis estadistico con interpretacion
- [x] Media, mediana, std, minimo, maximo (ydata_profiling)
- [ ] **Rangos intercuartilicos (Q1, Q2, Q3, IQR) con tabla e interpretacion** *(pendiente — exigido explicitamente por el taller)*
- [x] Distribucion de isFraud: 99.87% no fraude / 0.13% fraude

### 2d. Visualizaciones
- [ ] **Histogramas con solapamiento fraude vs no-fraude** *(pendiente — exigido explicitamente: "ver si estas estan relacionadas")*
- [x] **Correlacion** — heatmap (identificar multicolinealidades)
- [x] **Boxplots** por variable numerica
- [ ] **Distribucion de `type` vs `isFraud`** (countplot) *(pendiente)*
- [x] Correlaciones con isFraud ordenadas
- [x] Hallazgo documentado: solo TRANSFER y CASH_OUT tienen fraude

---

## PUNTO 3 — Preparacion de los Datos

> El taller exige: transformaciones + 3 bases balanceadas. **Para cada base repetir el analisis del Punto 2.**

### 3.1 Transformaciones
- [x] Eliminar: `nameOrig`, `nameDest`, `isFlaggedFraud`
- [x] Encoding: `type` → one-hot encoding
- [x] Feature engineering: `hour`, `hour_sin`, `hour_cos`, `error_balance_orig`, `error_balance_dest`
- [x] Transformacion logaritmica para outliers
- [x] Split train/test 80/20 con `stratify=y`
- [x] StandardScaler POST-SPLIT (anti data leakage)

### 3.2 Base 1 — Undersampling
- [x] `RandomUnderSampler(random_state=42)`
- [x] Tamano documentado
- [x] EDA Punto 2: distribucion de clases + histograma amount_log
- [ ] EDA Punto 2 completo (estadistica descriptiva, IQR, countplot type) *(parcial)*

### 3.3 Base 2 — Oversampling
- [x] `RandomOverSampler(random_state=42)`
- [x] Tamano documentado
- [x] EDA Punto 2: distribucion de clases + histograma amount_log
- [ ] EDA Punto 2 completo *(parcial)*

### 3.4 Base 3 — SMOTE
- [x] `SMOTE(random_state=42)`
- [x] Tamano documentado
- [x] EDA Punto 2: distribucion de clases + histograma amount_log
- [ ] EDA Punto 2 completo *(parcial)*

---

## PUNTO 4 — Modelado

> El taller exige: 3 modelos x 3 datasets. CatBoost con hiperparametros **justificados con fuentes cientificas** segun resultados previos.

### 4a. Regresion Logistica *(el taller dice "lineal" pero corresponde a Logistica)*
- [x] Entrenar sobre Undersampling, Oversampling y SMOTE
- [x] Tres puntos de corte: 0.2, 0.5 y 0.78
- [x] Tabla comparativa consolidada con metricas y ROC-AUC

### 4b. Random Forest
- [x] `n_estimators = 100` sobre los 3 datasets
- [x] `n_estimators = 500` sobre los 3 datasets
- [x] `class_weight='balanced'`
- [x] `bootstrap=True`
- [x] `max_features='sqrt'`
- [x] Evaluar con thresholds 0.2, 0.5, 0.78
- [x] Tabla comparativa con ROC-AUC

### 4c. CatBoost
- [x] Hiperparametros seleccionados segun resultados previos
- [x] **Justificacion de cada hiperparametro con fuente cientifica:**
  - `iterations=300` — justificado: balance capacidad/tiempo (refs. 2, 3 del marco teorico)
  - `learning_rate=0.05` — justificado: tasa conservadora evita overfitting en GBDT (ref. 43)
  - `depth=6` — justificado: profundidad optima reportada para datos financieros desbalanceados (ref. 1)
  - `eval_metric='F1'` — justificado: metrica adecuada para clases desbalanceadas (ref. 2)
  - Sin `scale_pos_weight` con SMOTE/Over — justificado: doble penalizacion (IJSDR2401084, ResearchGate 349156860)
- [x] Entrenar sobre los 3 datasets
- [x] Evaluar con thresholds 0.2, 0.5, 0.78
- [x] Tabla comparativa con ROC-AUC

### Metricas registradas
- [x] Matriz de confusion (TP, FP, TN, FN)
- [x] Precision, Recall, F1-score
- [x] ROC-AUC (valor numerico)
- [ ] Curva ROC grafica *(pendiente)*
- [ ] Curva Precision-Recall *(pendiente)*

---

## PUNTO 5 — Evaluacion con KPI Ganancia Neta

> El taller exige: usar mejores modelos con puntos de corte, calcular GN = (TP x $I) - (FP x $C), indicar cual tiene mayor GN y explicar por que.

```
GN = (TP x $100) - (FP x $33)
$I = 100  |  $C = 33
```

- [x] Calcular GN para todas las combinaciones (27 configs)
- [x] Tabla comparativa completa ordenada por GN
- [x] Identificar modelo con mayor GN: **RF (n=100) + Undersampling + threshold=0.78 (~$12.900)**
- [x] Explicar por que ese modelo maximiza la GN (justificacion tecnica + legal + citada)
- [x] Visualizacion: Top 15 configuraciones + GN maxima por modelo
- [x] Trade-off threshold analizado (0.2 / 0.5 / 0.78 con implicaciones legales)
- [x] Hallazgo critico: Regresion Logistica con GN negativa — explicado y citado

---

## PUNTO 6 — Analisis Etico

> El taller exige: analisis etico de aplicar IA con la organizacion seleccionada. **Citacion de materiales usados.**

- [x] FAccT framework introducido y citado
- [x] Sesgo algoritmico: thin-file, poblaciones vulnerables, Art. 15 CN
- [x] Privacidad y Habeas Data: Art. 15 CN, Ley 1266/2008
- [x] Problema caja negra: RF y CatBoost inescrutables — SHAP y LIME como solucion
- [x] Responsabilidad por FP: Art. 2341 CC, Sentencia T-255/22
- [x] Citas legales integradas en analisis de resultados (celda 112)
- [ ] **PENDIENTE: Seccion 6 independiente y desarrollada en el notebook** *(actualmente distribuido en celdas 1.4-1.6)*

---

## INFORME FINAL

> Formato academico de doble columna. Debe incluir resumen (abstract) y conclusiones.

- [ ] Resumen (abstract)
- [ ] Introduccion con contexto (Euromonitor citado)
- [ ] Punto 1 — Entendimiento del negocio
- [ ] Punto 2 — EDA con figuras
- [ ] Punto 3 — Balanceo + EDA por dataset
- [ ] Punto 4 — Modelos con tablas de metricas y justificacion hiperparametros
- [ ] Punto 5 — Ganancia Neta con tabla y grafico
- [ ] Punto 6 — Analisis etico citado
- [ ] Conclusiones
- [ ] Referencias (formato APA o IEEE — 98 fuentes del marco teorico + adicionales)

---

## Pendientes priorizados

| # | Pendiente | Punto del taller | Urgencia |
|---|-----------|-----------------|----------|
| 1 | Seccion 6 etica independiente | Punto 6 | Alta |
| 2 | Histogramas solapamiento fraude vs no-fraude | Punto 2d | Alta |
| 3 | IQR y rangos intercuartilicos con tabla | Punto 2c | Alta |
| 4 | Countplot `type` vs `isFraud` | Punto 2d | Alta |
| 5 | EDA completo para cada dataset balanceado | Punto 3 | Media |
| 6 | Curva ROC grafica | Punto 4 | Media |
| 7 | Citas especificas Banco Falabella (fuentes verificables) | Punto 1.3 | Media |
| 8 | Informe final doble columna con abstract y conclusiones | Informe | Alta |

---

## Notas importantes
- El taller dice "Regresion lineal" pero corresponde a **Regresion Logistica**
- La seleccion de hiperparametros de CatBoost debe estar justificada con papers cientificos que ya resolvieron el mismo problema (IJSDR2401084, ResearchGate 349156860, refs. 1-3 del marco teorico)
- Toda afirmacion en el informe debe tener cita — incluida la seleccion de entidad financiera
- Fuente obligatoria de contexto: https://www.portal.euromonitor.com/magazine/homemain
