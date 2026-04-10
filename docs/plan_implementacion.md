# Plan de Implementacion — Deteccion de Fraude
**Proyecto:** Taller Grupal | Javeriana IA Modulo 4
**Entidad:** Banco Falabella | **Dataset:** PaySim
**Metodologia:** CRISP-DM
**Notebook unico:** `Evaluación_sumativa_grupal_–_Detección_de_fraude.ipynb`
**Fuente de contexto obligatoria:** https://www.portal.euromonitor.com/magazine/homemain

---

## FASE 1 — Setup y verificacion inicial

- [x] Instalar librerias: `imbalanced-learn`, `catboost`, `ydata-profiling==4.9.0`
- [x] Cargar dataset con chunked reading (471MB — evita MemoryError en 8GB RAM)
- [x] Muestreo estratificado 500.000 filas (misma distribucion 0.13% fraude)
- [x] Confirmar desbalance: `isFraud` ~0.13%

---

## FASE 2 — Punto 1: Entendimiento del Negocio

> **Regla del taller:** toda la informacion debe estar citada de fuentes confiables y relevantes.

### 2.1 Contexto del caso
- [x] Descripcion del problema de fraude financiero
- [x] Datos de mercado citados: Euromonitor 2024-2025 (perdidas >$33.5B USD, m-commerce +250%)

### 2.2 Marco legal colombiano
- [x] Arts. 246, 316, 323, 327 — Codigo Penal (Ley 599/2000)
- [x] Art. 2341 — Codigo Civil (restiticion de fondos por FN)
- [x] Art. 15 — Constitucion (Habeas Data — FP vulnera derechos)
- [x] Ley 1266/2008, Ley 1328/2009, Circular SFC 29/2014, Sentencia T-255/22
- [x] Como afecta al usuario + debido proceso (3 dimensiones: tecnica, operacional, legal)

### 2.3 Entidad financiera: Banco Falabella
- [x] Elementos financieros, tecnicos y operacionales
- [ ] Citas especificas verificables (reporte anual Grupo Falabella, SFC) *(pendiente)*

### 2.4 Etica
- [x] FAccT framework (Fairness, Accountability, Transparency) — citado
- [x] Sesgo algoritmico, caja negra, SHAP y LIME como solucion

---

## FASE 3 — Punto 2: Entendimiento de los Datos

> Aplicar sobre el dataset **original sin balancear**. El taller exige interpretacion de cada resultado.

### 3.1 Estructura y calidad
- [x] Shape, dtypes, `df.info()`
- [x] Distribucion `isFraud` con grafico
- [x] Reporte automatizado `ydata_profiling` → `docs/eda_report.html`
- [ ] Valores unicos por categorica + duplicados *(pendiente)*

### 3.2 Estadistica descriptiva con interpretacion
- [x] Media, mediana, std, min, max
- [ ] **Q1, Q2, Q3, IQR por variable con tabla e interpretacion** *(pendiente — exigido por taller)*
- [x] Hallazgo: solo TRANSFER y CASH_OUT tienen fraude

### 3.3 Visualizaciones obligatorias
- [ ] **Histogramas con `hue=isFraud`** — solapamiento fraude vs no-fraude *(pendiente)*
- [x] Matriz de correlacion — multicolinealidades identificadas
- [x] Boxplots por variable
- [ ] **Countplot `type` vs `isFraud`** *(pendiente)*
- [x] Correlaciones con `isFraud` ordenadas

---

## FASE 4 — Punto 3: Preparacion de los Datos

> El taller exige: transformaciones + 3 bases balanceadas + **repetir Punto 2 en cada base**.

### 4.1 Preprocesamiento
- [x] Eliminar: `nameOrig`, `nameDest`, `isFlaggedFraud`
- [x] One-hot encoding de `type`
- [x] Feature engineering: `hour`, `hour_sin`, `hour_cos`, `error_balance_orig`, `error_balance_dest`
- [x] Transformacion logaritmica (outliers en `amount` y balances)
- [x] Split train/test 80/20 estratificado
- [x] StandardScaler POST-SPLIT (anti data leakage — fit solo sobre X_train)

### 4.2 Dataset 1 — Undersampling
- [x] `RandomUnderSampler(random_state=42)`
- [x] Tamano documentado
- [x] EDA basico: distribucion de clases + histograma `amount_log`
- [ ] EDA completo Punto 2 (IQR, countplot, estadistica con interpretacion) *(pendiente)*

### 4.3 Dataset 2 — Oversampling
- [x] `RandomOverSampler(random_state=42)`
- [x] Tamano documentado
- [x] EDA basico
- [ ] EDA completo Punto 2 *(pendiente)*

### 4.4 Dataset 3 — SMOTE
- [x] `SMOTE(random_state=42)`
- [x] Tamano documentado
- [x] EDA basico
- [ ] EDA completo Punto 2 *(pendiente)*

---

## FASE 5 — Punto 4: Modelado

> **Regla critica del taller:** los hiperparametros de CatBoost deben estar **justificados con fuentes cientificas** que ya resolvieron el mismo problema.

### 5.1 Regresion Logistica *(el taller dice "lineal" pero es logistica)*
- [x] Entrenar sobre los 3 datasets
- [x] Thresholds: 0.2, 0.5, 0.78
- [x] Tabla comparativa con TP, FP, FN, Precision, Recall, F1, ROC-AUC → `df_lr`

### 5.2 Random Forest
- [x] `n_estimators=100` y `n_estimators=500` sobre los 3 datasets
- [x] `class_weight='balanced'`, `bootstrap=True`, `max_features='sqrt'`
- [x] Thresholds: 0.2, 0.5, 0.78
- [x] Tabla comparativa con ROC-AUC → `df_rf`

### 5.3 CatBoost — justificacion de hiperparametros con papers
> El taller exige escoger hiperparametros segun resultados previos y **justificarlos debidamente**.
> Estrategia: citar papers que ya resolvieron el mismo problema de fraude con CatBoost.

| Hiperparametro | Valor | Fuente cientifica que lo justifica |
|----------------|-------|-------------------------------------|
| `iterations` | 300 | Balance capacidad/tiempo en datos financieros — refs. 2, 3 marco teorico; IJSDR2401084 |
| `learning_rate` | 0.05 | Tasa conservadora evita sobreajuste en GBDT secuencial — ref. 43; ResearchGate 349156860 |
| `depth` | 6 | Profundidad optima para datos financieros desbalanceados — ref. 1; AUC 0.9837 reportado |
| `eval_metric` | F1 | Metrica correcta para clases desbalanceadas (evita Accuracy Paradox) — ref. 2; MDPI 2078-2489 |
| Sin `scale_pos_weight` (SMOTE/Over) | — | SMOTE y scale_pos_weight son estrategias alternativas — aplicar ambas genera doble penalizacion — IJSDR2401084 |

- [x] Justificacion implementada en markdown del notebook (celda 104)
- [x] Entrenar sobre los 3 datasets
- [x] Thresholds: 0.2, 0.5, 0.78
- [x] Tabla comparativa con ROC-AUC → `df_cb`

### 5.4 Metricas
- [x] Matriz de confusion, Precision, Recall, F1, ROC-AUC (numerico)
- [ ] Curva ROC grafica *(pendiente)*
- [ ] Curva Precision-Recall *(pendiente)*

---

## FASE 6 — Punto 5: Evaluacion Ganancia Neta

```
GN = (TP x $100) - (FP x $33)
```

- [x] Calcular GN para las 27 combinaciones
- [x] Tabla comparativa ordenada por GN
- [x] Ganador: **RF (n=100) + Undersampling + threshold=0.78 (~$12.900)**
- [x] Explicacion del ganador — justificacion tecnica + legal + citada
- [x] Visualizacion Top 15 + GN maxima por modelo
- [x] Trade-off threshold analizado con implicaciones legales
- [x] Hallazgo critico: LR con GN negativa — explicado y citado

---

## FASE 7 — Punto 6: Analisis Etico

> El taller exige analisis etico con la organizacion seleccionada. **Citacion obligatoria de todos los materiales.**

- [x] FAccT framework citado
- [x] Sesgo algoritmico: thin-file, discriminacion, Art. 15 CN
- [x] SHAP y LIME como solucion XAI
- [x] Responsabilidad por FP y FN con articulos legales
- [x] Citas integradas en analisis de resultados
- [ ] **Seccion 6 independiente y desarrollada en el notebook** *(pendiente)*

---

## FASE 8 — Informe Final

> Formato academico doble columna. Obligatorio: resumen (abstract) y conclusiones.

- [ ] Abstract (resumen ejecutivo)
- [ ] Introduccion con contexto y Euromonitor citado
- [ ] Punto 1: Marco legal + Banco Falabella + etica
- [ ] Punto 2: EDA con figuras del notebook
- [ ] Punto 3: Balanceo + EDA por dataset balanceado
- [ ] Punto 4: Modelos con tablas de metricas + **justificacion hiperparametros CatBoost con papers**
- [ ] Punto 5: Ganancia Neta con tabla comparativa y grafico
- [ ] Punto 6: Analisis etico citado
- [ ] Conclusiones
- [ ] Referencias en formato APA o IEEE

---

## Pendientes priorizados

| # | Tarea | Fase | Urgencia |
|---|-------|------|----------|
| 1 | Histogramas solapamiento fraude vs no-fraude (`hue=isFraud`) | Fase 3 | Alta |
| 2 | IQR y rangos intercuartilicos con tabla e interpretacion | Fase 3 | Alta |
| 3 | Countplot `type` vs `isFraud` | Fase 3 | Alta |
| 4 | Seccion 6 etica independiente en notebook | Fase 7 | Alta |
| 5 | EDA completo para cada dataset balanceado | Fase 4 | Media |
| 6 | Curva ROC grafica | Fase 5 | Media |
| 7 | Citas especificas Banco Falabella (reporte anual, SFC) | Fase 2 | Media |
| 8 | Informe final doble columna con abstract y conclusiones | Fase 8 | Alta |

---

## Bugs criticos — TODOS RESUELTOS

| Bug | Solucion aplicada |
|-----|------------------|
| `isFlaggedFraud` no eliminada | Celda 47: eliminada del pipeline |
| Data leakage — scaler antes del split | Celda 67: StandardScaler fit solo sobre X_train |
| LR con split interno | Celda 91: usa X_test global fijo |
| RF n=500 sin ejecutar | Celda 102: tabla completa n=100/500 |
| CatBoost sin ejecutar | Celda 107: 3 datasets x 3 thresholds |
| Punto 5 Ganancia Neta no existia | Celdas 109-112: completo con analisis citado |
| MemoryError al cargar 6.3M filas | Chunked reading + dtypes optimizados + muestra 500k |
| ydata-profiling conflicto IPython | Guardado como HTML en docs/ |

---

## Convencion de variables (para consistencia en todo el notebook)

```python
# DataFrames
df_original, df_fraude, df_sample

# Datasets balanceados
X_under, y_under          # Undersampling
X_train_over, y_train_over  # Oversampling
X_train_smote, y_train_smote  # SMOTE

# Modelos
lr_model, rf_model, cb_model

# Resultados
df_lr, df_rf, df_cb, df_todos  # Para tabla Ganancia Neta
```
