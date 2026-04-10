# Plan de Implementacion — Deteccion de Fraude
**Proyecto:** Taller Grupal | Javeriana IA Modulo 4
**Entidad:** Banco Falabella | **Dataset:** PaySim
**Metodologia:** CRISP-DM

---

## Fases del Plan

### FASE 1 — Setup y verificacion inicial
**Notebook:** ninguno (preparacion)

- [ ] Verificar instalacion de librerias (`pip install -r requirements.txt`)
- [ ] Cargar dataset y confirmar que lee correctamente
- [ ] Confirmar tamanno: ~6.3M filas, 11 columnas
- [ ] Confirmar desbalance: `isFraud` ~0.13%

**Librerias requeridas:**
```
pandas, numpy, matplotlib, seaborn, scikit-learn,
imbalanced-learn, catboost, jupyter
```

---

### FASE 2 — EDA Dataset Original
**Notebook:** `01_eda.ipynb`
**Taller:** Punto 2

#### 2.1 Estructura de los datos
- [ ] Shape, dtypes, valores unicos
- [ ] Valores nulos y duplicados
- [ ] Distribucion `isFraud` (tabla + grafico de barras)

#### 2.2 Estadistica descriptiva
- [ ] `df.describe()` completo con interpretacion
- [ ] Minimo, maximo, media, mediana, std
- [ ] Q1, Q2, Q3, IQR por variable numerica
- [ ] Identificar outliers via IQR

#### 2.3 Visualizaciones
- [ ] Histogramas por variable — con hue `isFraud` (solapamiento fraude vs no fraude)
- [ ] Boxplots por variable — con hue `isFraud`
- [ ] Matriz de correlacion (heatmap) — identificar multicolinealidades
- [ ] Distribucion de `type` vs `isFraud` (countplot)
- [ ] Distribucion de `amount` por tipo de transaccion

#### 2.4 Hallazgos clave a documentar
- [ ] Solo tipos `TRANSFER` y `CASH_OUT` tienen fraude → justificar en preprocesamiento
- [ ] `isFlaggedFraud` es casi siempre 0 → eliminar
- [ ] Alta correlacion entre variables de balance → documentar

---

### FASE 3 — Preparacion y Balanceo
**Notebook:** `02_balanceo.ipynb`
**Taller:** Punto 3

#### 3.1 Preprocesamiento base (aplicar a los 3 datasets)
- [ ] Eliminar: `nameOrig`, `nameDest`, `isFlaggedFraud`
- [ ] Encoding: `type` → one-hot encoding (`pd.get_dummies`)
- [ ] Split train/test: 80/20, `stratify=y`, `random_state=42`
- [ ] **IMPORTANTE:** Balanceo SOLO sobre train, test queda intacto

#### 3.2 Dataset 1 — Undersampling
- [ ] Aplicar `RandomUnderSampler(random_state=42)`
- [ ] Documentar tamanno resultante
- [ ] Repetir EDA completo (Punto 2) sobre este dataset
- [ ] Guardar como `X_train_under`, `y_train_under`

#### 3.3 Dataset 2 — Oversampling
- [ ] Aplicar `RandomOverSampler(random_state=42)`
- [ ] Documentar tamanno resultante
- [ ] Repetir EDA completo (Punto 2) sobre este dataset
- [ ] Guardar como `X_train_over`, `y_train_over`

#### 3.4 Dataset 3 — SMOTE
- [ ] Aplicar `SMOTE(random_state=42)`
- [ ] Documentar tamanno resultante
- [ ] Repetir EDA completo (Punto 2) sobre este dataset
- [ ] Guardar como `X_train_smote`, `y_train_smote`

---

### FASE 4 — Modelado
**Notebook:** `03_modelos.ipynb`
**Taller:** Punto 4

> Entrenar cada modelo sobre los 3 datasets = 9 combinaciones

#### 4.1 Estructura de resultados
```python
results = {}
# Clave: "modelo_dataset_threshold"
# Valor: {"TP": , "FP": , "TN": , "FN": , "precision": , "recall": , "f1": , "auc": , "GN": }
```

#### 4.2 Regresion Logistica
- [ ] Entrenar sobre `under`, `over`, `smote`
- [ ] Para cada dataset, evaluar con thresholds: `[0.2, 0.5, 0.78]`
- [ ] Registrar resultados en `results`

#### 4.3 Random Forest
- [ ] Entrenar con `n_estimators=100` sobre los 3 datasets
- [ ] Entrenar con `n_estimators=500` sobre los 3 datasets
- [ ] Evaluar con thresholds: `[0.2, 0.5, 0.78]`
- [ ] Registrar resultados en `results`

#### 4.4 CatBoost
- [ ] Definir hiperparametros y justificarlos en markdown
- [ ] Entrenar sobre los 3 datasets
- [ ] Evaluar con thresholds: `[0.2, 0.5, 0.78]`
- [ ] Registrar resultados en `results`

---

### FASE 5 — Evaluacion y Ganancia Neta
**Notebook:** `04_evaluacion_ganancia.ipynb`
**Taller:** Punto 5

- [ ] Calcular `GN = TP*100 - FP*33` para todas las combinaciones
- [ ] Construir tabla comparativa completa (modelo x dataset x threshold)
- [ ] Graficar Ganancia Neta por configuracion (barplot)
- [ ] Identificar la combinacion ganadora
- [ ] Redactar explicacion: por que ese modelo/dataset/threshold maximiza GN
- [ ] Discutir trade-off Recall vs Precision en terminos de negocio

---

### FASE 6 — Informe Final
**Herramienta:** Word / LaTeX (formato doble columna)

- [ ] Resumen (abstract)
- [ ] Introduccion (contexto Banco Falabella + fraude financiero)
- [ ] Punto 1: Marco legal + entidad
- [ ] Punto 2: EDA (figuras del notebook 01)
- [ ] Punto 3: Balanceo (figuras del notebook 02)
- [ ] Punto 4: Modelado (tablas de metricas)
- [ ] Punto 5: Ganancia Neta (tabla comparativa + grafico)
- [ ] Punto 6: Analisis etico
- [ ] Conclusiones
- [ ] Referencias (98 fuentes del marco teorico + adicionales)

---

## Orden de Ejecucion Recomendado

```
1. requirements.txt  →  pip install
2. 01_eda.ipynb      →  EDA completo dataset original
3. 02_balanceo.ipynb →  3 datasets + EDA de cada uno
4. 03_modelos.ipynb  →  9 combinaciones entrenadas
5. 04_evaluacion_ganancia.ipynb → KPI final
6. Informe Word/LaTeX
```

---

## Advertencias Tecnicas

| Riesgo | Mitigacion |
|--------|-----------|
| Dataset muy grande (6.3M filas) para SMOTE | Usar subset para SMOTE o reducir con undersampling previo |
| Overfitting en Oversampling | Validar siempre en test sin balancear |
| CatBoost lento sin GPU | Usar `task_type='CPU'`, reducir `iterations` si es necesario |
| Threshold 0.2 puede dar muchos FP | Documentar el trade-off, es el punto del taller |
