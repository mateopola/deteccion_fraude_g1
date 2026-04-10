# Entregables - Deteccion de Fraude
**Especializacion en IA | Modulo 4 | Pontificia Universidad Javeriana**
**Metodologia:** CRISP-DM
**Dataset:** PaySim - Synthetic Financial Datasets For Fraud Detection (Kaggle)

---

## PUNTO 1 — Entendimiento del Negocio

### 1.1 Contexto del caso
- [x] Descripcion del problema de fraude financiero *(celda 1.2 del notebook)*
- [ ] Relevancia del problema en el sector financiero con datos de mercado *(falta citar Euromonitor — perdidas >$33.5B USD, crecimiento m-commerce 250%)*

### 1.2 Marco legal (Colombia)
- [x] **Art. 246 Codigo Penal** — Estafa *(celda 1.4)*
- [x] **Art. 316 Codigo Penal** — Captacion masiva de dineros *(celda 1.4)*
- [x] **Art. 323 Codigo Penal** — Lavado de activos + SARLAFT *(celda 1.4)*
- [x] **Art. 327 Codigo Penal** — Enriquecimiento ilicito *(celda 1.4)*
- [x] **Art. 2341 Codigo Civil** — Responsabilidad civil extracontractual *(celda 1.4)*
- [x] **Art. 15 Constitucion Politica** — Habeas Data *(celda 1.4)*
- [x] Otros articulos relevantes: Ley 1266/2008, Ley 1328/2009, Circular SFC 29/2014 *(celda 1.4)*
- [x] Como afecta al usuario cada norma *(descrito en cada articulo)*
- [x] Cual seria el debido proceso de la organizacion ante un caso de fraude *(celda 1.5 — 3 dimensiones)*

### 1.3 Entidad financiera seleccionada: **Banco Falabella**
- [x] Describir sus elementos **financieros** relevantes *(celda 1.3 — perfil financiero, CMR, segmento)*
- [x] Describir sus elementos **tecnicos** *(celda 1.3 — app, web, Visa/Mastercard, tiempo real)*
- [x] Describir sus elementos **operacionales** *(celda 1.3 — SARLAFT, canales digitales, bloqueo/reactivacion)*
- [ ] Toda la informacion debe estar citada de fuentes confiables
  - **PENDIENTE:** agregar citas especificas (reporte Falabella, SFC, noticias sectoriales)

### 1.4 Etica en la toma de decisiones
- [x] Como la toma de decisiones automatizada implica un tema etico *(celda 1.6 — FAccT, sesgo, caja negra)*
- [x] Introduccion etica desarrollada *(se profundiza en Punto 6)*

---

## PUNTO 2 — Entendimiento de los Datos

> Aplicar sobre el dataset original (sin balancear)

### 2a. Tamanno de la base de datos
- [x] Numero de filas y columnas *(6.362.620 filas x 11 columnas — ejecutado, celda 11)*
- [x] Descripcion de cada variable *(diccionario completo en celda 6)*

### 2b. Calidad de los datos
- [ ] Valores faltantes por columna *(pandas_profiling corre pero no hay celda explicita — verificar)*
- [ ] Tipos de variables explicitamente documentados *(esta en profiling pero falta celda dedicada)*
- [ ] Valores unicos por variable categorica *(falta)*
- [ ] Duplicados *(falta celda explicita)*

### 2c. Analisis estadistico descriptivo
- [x] Media, mediana, desviacion estandar *(pandas_profiling — celda 20)*
- [x] Minimo, maximo *(pandas_profiling — celda 20)*
- [ ] Percentiles Q1, Q2, Q3 e IQR explicitamente *(el profiling los incluye pero falta tabla dedicada con interpretacion)*
- [ ] Interpretacion de los resultados por variable *(falta texto explicativo por variable)*
- [x] Distribucion de `isFraud` — 99.87% no fraude / 0.13% fraude *(celda 15/47)*

### 2d. Visualizaciones
- [ ] **Histogramas** comparando fraude vs no fraude *(hay histogramas pero sin hue=isFraud — falta solapamiento)*
- [x] **Matriz de correlacion** *(heatmap ejecutado — celda 23)*
- [x] **Boxplots** por variable *(celda 21 — ejecutado)*
- [ ] Distribucion de `type` vs `isFraud` *(falta countplot de tipo de transaccion)*
- [x] Correlaciones con `isFraud` *(celda 45 — ordenadas)*

---

## PUNTO 3 — Preparacion de los Datos

### 3.1 Transformaciones generales
- [x] Encoding `type` → one-hot encoding *(celda 35)*
- [ ] Eliminacion `nameOrig`, `nameDest`, `isFlaggedFraud` — **BUG: `isFlaggedFraud` NO fue eliminada** *(sigue en celda 44)*
- [x] Tratamiento de outliers — transformacion logaritmica *(celdas 27-28)*
- [x] Estandarizacion con StandardScaler *(celda 29)* — **ADVERTENCIA: scaler aplicado antes del split (data leakage)**
- [x] Feature engineering: `hour`, `hour_sin`, `hour_cos`, `error_balance_orig`, `error_balance_dest` *(celdas 31-39)*

### 3.2 Tres bases de datos balanceadas
> Muestra de 500.000 registros (estratificada) — justificado por recursos computacionales

#### Base 1 — Undersampling
- [x] Aplicar RandomUnderSampler *(celda 54)*
- [ ] Documentar tamanno resultante *(falta print del shape)*
- [ ] Repetir analisis Punto 2 *(NO realizado)*

#### Base 2 — Oversampling
- [x] Aplicar RandomOverSampler *(celda 56)*
- [ ] Documentar tamanno resultante *(falta print del shape)*
- [ ] Repetir analisis Punto 2 *(NO realizado)*

#### Base 3 — SMOTE
- [x] Aplicar SMOTE *(celda 58)*
- [ ] Documentar tamanno resultante *(falta print del shape)*
- [ ] Repetir analisis Punto 2 *(NO realizado)*

---

## PUNTO 4 — Modelado

> Entrenar cada modelo sobre las 3 bases de datos (9 combinaciones en total)

### 4a. Regresion Logistica
- [x] Entrenar sobre Undersampling *(celda 61)*
- [x] Entrenar sobre Oversampling *(celda 62)*
- [x] Entrenar sobre SMOTE *(celda 63)*
- [x] Evaluar con thresholds 0.2 | 0.5 | 0.78 *(celdas 61-63)*
- [ ] Tabla comparativa consolidada *(celda 65 tiene bug — hace split interno, resultados no comparables)*

### 4b. Random Forest
- [x] `class_weight='balanced'`, `bootstrap=True`, `max_features='sqrt'` *(celdas 68-70)*
- [x] n_estimators=100 sobre los 3 datasets *(celdas 68-70 ejecutadas)*
- [ ] n_estimators=500 sobre los 3 datasets *(no ejecutado)*
- [ ] Tabla comparativa consolidada *(celda 72 — exec=None, sin ejecutar)*
- [ ] Evaluar con 3 thresholds *(la funcion evaluar_rf no aplica thresholds dinamicos)*

### 4c. CatBoost
- [ ] Justificar hiperparametros *(hay markdown pero celda 75 exec=None)*
- [ ] Entrenar modelo *(celda 75 sin ejecutar)*
- [ ] Evaluar con 3 thresholds *(celda 77 sin ejecutar)*

### Metricas a registrar
- [x] Matriz de confusion *(en celdas de LR y RF)*
- [x] Precision, Recall, F1-score *(en celdas de LR y RF)*
- [ ] ROC-AUC *(no calculado en ninguna celda)*
- [ ] Curva Precision-Recall *(no generada)*

---

## PUNTO 5 — Evaluacion con KPI Ganancia Neta

```
Ganancia Neta = (TP * $100) - (FP * $33)
```

- [ ] Calcular Ganancia Neta para cada combinacion *(NO existe en el notebook)*
- [ ] Tabla comparativa completa *(NO existe)*
- [ ] Identificar modelo con mayor Ganancia Neta *(NO existe)*
- [ ] Explicar por que ese modelo es el mejor *(NO existe)*
- [ ] Discutir trade-off Recall vs Precision *(NO existe)*

---

## PUNTO 6 — Analisis Etico — **Banco Falabella**

- [x] Implicaciones eticas — FAccT introducido *(celda 1.6)*
- [x] Sesgo algoritmico — thin-file, discriminacion *(celda 1.6)*
- [x] Privacidad y Habeas Data — Art. 15, Ley 1266/2008 *(celda 1.4)*
- [x] Transparencia y explicabilidad — SHAP, LIME *(celda 1.6)*
- [x] Responsabilidad por falsos positivos *(celda 1.5)*
- [ ] Toda afirmacion citada con fuente especifica en el notebook *(faltan citas inline)*

---

## INFORME FINAL

### Formato
- [ ] Doble columna (formato academico)
- [ ] Citacion de todas las fuentes (definir APA o IEEE)

### Secciones obligatorias
- [x] Introduccion / contexto
- [ ] Resumen (abstract)
- [x] Punto 1 — Entendimiento del negocio *(en notebook)*
- [ ] Punto 2 — Entendimiento de los datos *(incompleto)*
- [ ] Punto 3 — Preparacion de los datos *(bugs pendientes)*
- [ ] Punto 4 — Modelado *(incompleto)*
- [ ] Punto 5 — Evaluacion *(no existe)*
- [ ] Punto 6 — Analisis etico *(parcial)*
- [ ] Conclusiones
- [ ] Referencias bibliograficas

---

## Bugs criticos pendientes

| # | Bug | Impacto | Celda |
|---|-----|---------|-------|
| 1 | `isFlaggedFraud` no eliminada | Variable sin valor predictivo contamina el modelo | 37/42 |
| 2 | StandardScaler aplicado antes del split | **Data leakage** — resultados inflados | 29/40 |
| 3 | `evaluar_modelo` LR hace split interno | Resultados de LR no comparables entre si | 65 |
| 4 | RF n_estimators=500 no ejecutado | Falta la mitad del punto 4b | 72 |
| 5 | CatBoost sin ejecutar | Punto 4c incompleto | 74-77 |
| 6 | Punto 5 (Ganancia Neta) no existe | Punto critico del taller — falta completo | — |

---

## Notas del equipo
- El taller menciona "Regresion lineal" pero corresponde a **Regresion Logistica**
- Fuente obligatoria: https://www.portal.euromonitor.com/magazine/homemain
- EDA sobre los 3 datasets balanceados es obligatorio (punto 3 lo exige explicitamente)
