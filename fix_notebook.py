"""
fix_notebook.py
Corrige los bugs del notebook segun la literatura de deteccion de fraude.
Orden: literatura primero, luego implementacion.
NO ejecutar en Colab - es para ejecucion local.
"""
import json, copy

PATH = 'c:/Users/mateo/Desktop/deteccion_fraude_grupo_1/Evaluación_sumativa_grupal_–_Detección_de_fraude.ipynb'

with open(PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

def code(src):
    return {"cell_type": "code", "metadata": {}, "source": src, "outputs": [], "execution_count": None}

def md(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src}

cells = nb['cells']

# ============================================================
# FIX 1 — Celda 33: Quitar scaler.fit_transform (data leakage)
# Solo definir columnas_numericas. El escalado se mueve post-split.
# Literatura: arXiv 2601.07276, Fraud Detection Handbook cap.6
# ============================================================
cells[33]['source'] = (
    "# Definicion de columnas numericas para escalar\n"
    "# NOTA: el escalado se aplica DESPUES del split train/test\n"
    "# para evitar data leakage (arXiv 2601.07276)\n"
    "columnas_numericas = [\n"
    '    "amount_log",\n'
    '    "oldbalanceOrg_log",\n'
    '    "newbalanceOrig_log",\n'
    '    "oldbalanceDest_log",\n'
    '    "newbalanceDest_log"\n'
    "]\n"
    "scaler = StandardScaler()  # se fitteara solo sobre X_train"
)

# ============================================================
# FIX 2 — Celda 41: Eliminar isFlaggedFraud
# Literatura: PaySim papers unanimes — variable del simulador,
# no disponible en produccion real (ref. 1, 2, 67)
# ============================================================
cells[41]['source'] = (
    "# Eliminacion de variables sin valor predictivo\n"
    "# nameOrig/nameDest: identificadores unicos, no generalizan\n"
    "# isFlaggedFraud: variable del simulador PaySim basada en reglas\n"
    "#   heuristicas, no disponible en produccion real (correlacion=0.078)\n"
    "#   Literatura: papers PaySim (ref. 1, 2, 67) la eliminan sistematicamente\n"
    'df_fraude = df_fraude.drop(columns=["nameOrig", "nameDest", "isFlaggedFraud"])'
)

# ============================================================
# FIX 3 — Celda 44: Quitar segundo scaler.fit_transform
# Solo agregar columnas a la lista. El escalado es post-split.
# ============================================================
cells[44]['source'] = (
    '# Agregar variables derivadas a la lista de columnas a escalar\n'
    'columnas_numericas.append("error_balance_dest")\n'
    'columnas_numericas.append("error_balance_orig")'
)

# ============================================================
# FIX 4 — Despues del split (celda 55): insertar escalado correcto
# fit SOLO sobre X_train, transform sobre ambos
# Literatura: Fraud Detection Handbook, scikit-learn docs (ref. 72)
# ============================================================
fix_scaler = code(
    "# ============================================================\n"
    "# ESCALADO POST-SPLIT — practica correcta segun la literatura\n"
    "# fit() solo sobre X_train para evitar data leakage\n"
    "# transform() sobre X_train y X_test por separado\n"
    "# Ref: Fraud Detection Handbook cap.6, arXiv 2601.07276\n"
    "# ============================================================\n"
    "X_train = X_train.copy()\n"
    "X_test  = X_test.copy()\n\n"
    "X_train[columnas_numericas] = scaler.fit_transform(X_train[columnas_numericas])\n"
    "X_test[columnas_numericas]  = scaler.transform(X_test[columnas_numericas])\n\n"
    "print('Escalado aplicado correctamente:')\n"
    "print(f'  X_train: {X_train.shape} | X_test: {X_test.shape}')"
)

# ============================================================
# FIX 5 — Documentar tamanos de los datasets balanceados
# La literatura exige documentar el resultado de cada tecnica
# ============================================================
doc_balanceo = code(
    "# Tamanos resultantes de cada tecnica de balanceo\n"
    "# Ref: Comparative Analysis Under/Over/SMOTE (MDPI 2078-2489)\n"
    "print('=== Distribucion de clases post-balanceo ===')\n"
    "import pandas as pd\n\n"
    "resumen = pd.DataFrame({\n"
    "    'Dataset': ['Train original', 'Undersampling', 'Oversampling', 'SMOTE'],\n"
    "    'Total filas': [\n"
    "        len(X_train),\n"
    "        len(X_under),\n"
    "        len(X_train_over),\n"
    "        len(X_train_smote)\n"
    "    ],\n"
    "    'Fraude (clase 1)': [\n"
    "        y_train.sum(),\n"
    "        y_under.sum(),\n"
    "        y_train_over.sum(),\n"
    "        y_train_smote.sum()\n"
    "    ],\n"
    "    'No fraude (clase 0)': [\n"
    "        (y_train == 0).sum(),\n"
    "        (y_under == 0).sum(),\n"
    "        (y_train_over == 0).sum(),\n"
    "        (y_train_smote == 0).sum()\n"
    "    ]\n"
    "})\n"
    "resumen['% Fraude'] = (resumen['Fraude (clase 1)'] / resumen['Total filas'] * 100).round(2)\n"
    "print(resumen.to_string(index=False))"
)

# ============================================================
# FIX 6 — EDA post-balanceo (punto 3 del taller lo exige)
# Estadisticas y distribucion de cada dataset balanceado
# Ref: Comparative Analysis (MDPI), Fraud Detection Handbook
# ============================================================
eda_balanceo = code(
    "# EDA POST-BALANCEO — requerido por el punto 3 del taller\n"
    "# La literatura recomienda verificar distribucion tras cada tecnica\n"
    "# Ref: MDPI 2078-2489, Fraud Detection Handbook cap.5\n\n"
    "fig, axes = plt.subplots(1, 3, figsize=(15, 4))\n"
    "datasets_bal = [\n"
    "    (y_under,        'Undersampling',  axes[0]),\n"
    "    (y_train_over,   'Oversampling',   axes[1]),\n"
    "    (y_train_smote,  'SMOTE',          axes[2]),\n"
    "]\n"
    "for y_bal, titulo, ax in datasets_bal:\n"
    "    counts = pd.Series(y_bal).value_counts()\n"
    "    ax.bar(['No fraude (0)', 'Fraude (1)'], counts.values,\n"
    "           color=['steelblue', 'tomato'], edgecolor='black')\n"
    "    ax.set_title(f'{titulo}\\n{counts[1]} fraudes / {counts[0]} no fraudes')\n"
    "    ax.set_ylabel('Frecuencia')\n"
    "    for j, v in enumerate(counts.values):\n"
    "        ax.text(j, v + counts.max()*0.01, f'{v:,}', ha='center', fontsize=9)\n\n"
    "plt.suptitle('Distribucion de clases por tecnica de balanceo', fontsize=13, y=1.02)\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

eda_stats_balanceo = code(
    "# Estadisticas descriptivas post-balanceo (variable amount_log)\n"
    "# Verificar que SMOTE no genero distribucion anormal\n"
    "# Ref: MDPI 2078-2489 — 'SMOTE puede generar ruido en zonas de solapamiento'\n\n"
    "fig, axes = plt.subplots(1, 3, figsize=(15, 4))\n"
    "col_idx = list(X_train.columns).index('amount_log') if 'amount_log' in X_train.columns else 0\n\n"
    "configs = [\n"
    "    (X_under,       y_under,       'Undersampling', axes[0]),\n"
    "    (X_train_over,  y_train_over,  'Oversampling',  axes[1]),\n"
    "    (X_train_smote, y_train_smote, 'SMOTE',         axes[2]),\n"
    "]\n"
    "for X_b, y_b, titulo, ax in configs:\n"
    "    col = 'amount_log' if 'amount_log' in X_b.columns else X_b.columns[col_idx]\n"
    "    df_tmp = pd.DataFrame({'amount_log': X_b[col], 'isFraud': y_b})\n"
    "    for label, color in [(0, 'steelblue'), (1, 'tomato')]:\n"
    "        subset = df_tmp[df_tmp['isFraud'] == label]['amount_log']\n"
    "        ax.hist(subset, bins=40, alpha=0.5, color=color,\n"
    "                label=f'Clase {label}', density=True)\n"
    "    ax.set_title(f'{titulo}\\nDistribucion amount_log')\n"
    "    ax.set_xlabel('amount_log (estandarizado)')\n"
    "    ax.legend()\n\n"
    "plt.suptitle('Solapamiento fraude vs no-fraude por tecnica', fontsize=13, y=1.02)\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

# ============================================================
# FIX 7 — Regresion Logistica: funcion con X_test fijo
# La literatura exige test set identico para comparar modelos
# Ref: Fraud Detection Handbook, MDPI 2078-2489
# ============================================================
lr_tabla_nueva = code(
    "# Tabla comparativa Regresion Logistica\n"
    "# Test set FIJO para todas las comparaciones (X_test, y_test global)\n"
    "# Ref: Fraud Detection Handbook — 'el test debe ser identico para comparar'\n\n"
    "from sklearn.metrics import roc_auc_score\n\n"
    "thresholds = [0.2, 0.5, 0.78]\n"
    "resultados_lr = []\n\n"
    "configs_lr = [\n"
    "    (X_under,       y_under,       'Undersampling'),\n"
    "    (X_train_over,  y_train_over,  'Oversampling'),\n"
    "    (X_train_smote, y_train_smote, 'SMOTE'),\n"
    "]\n\n"
    "for X_tr, y_tr, nombre in configs_lr:\n"
    "    modelo = LogisticRegression(max_iter=1000, random_state=42)\n"
    "    modelo.fit(X_tr, y_tr)\n"
    "    y_prob = modelo.predict_proba(X_test)[:, 1]\n"
    "    auc = roc_auc_score(y_test, y_prob)\n\n"
    "    for t in thresholds:\n"
    "        y_pred = (y_prob >= t).astype(int)\n"
    "        cm = confusion_matrix(y_test, y_pred)\n"
    "        tn, fp, fn, tp = cm.ravel()\n"
    "        resultados_lr.append({\n"
    "            'Modelo': 'Regresion Logistica',\n"
    "            'Balanceo': nombre,\n"
    "            'Threshold': t,\n"
    "            'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,\n"
    "            'Precision': round(precision_score(y_test, y_pred, zero_division=0), 4),\n"
    "            'Recall':    round(recall_score(y_test, y_pred, zero_division=0), 4),\n"
    "            'F1':        round(f1_score(y_test, y_pred, zero_division=0), 4),\n"
    "            'ROC-AUC':   round(auc, 4)\n"
    "        })\n\n"
    "df_lr = pd.DataFrame(resultados_lr)\n"
    "print('=== Resultados Regresion Logistica ===')\n"
    "print(df_lr[['Balanceo','Threshold','TP','FP','FN','Precision','Recall','F1','ROC-AUC']].to_string(index=False))"
)

# ============================================================
# FIX 8 — Random Forest: tabla completa con thresholds
# n_estimators 100 y 500, 3 datasets, 3 thresholds
# Ref: arXiv 2303.06514, IEEE 10533119
# ============================================================
rf_tabla_nueva = code(
    "# Tabla comparativa Random Forest\n"
    "# n_estimators: 100 y 500 | 3 datasets | 3 thresholds\n"
    "# Ref: arXiv 2303.06514 — RF con class_weight balanced para datos desbalanceados\n\n"
    "resultados_rf = []\n\n"
    "configs_rf = [\n"
    "    (X_under,       y_under,       'Undersampling'),\n"
    "    (X_train_over,  y_train_over,  'Oversampling'),\n"
    "    (X_train_smote, y_train_smote, 'SMOTE'),\n"
    "]\n\n"
    "for X_tr, y_tr, nombre in configs_rf:\n"
    "    for n_est in [100, 500]:\n"
    "        print(f'Entrenando RF n={n_est} | {nombre}...')\n"
    "        modelo = RandomForestClassifier(\n"
    "            n_estimators=n_est,\n"
    "            class_weight='balanced',\n"
    "            bootstrap=True,\n"
    "            max_features='sqrt',\n"
    "            random_state=42,\n"
    "            n_jobs=-1\n"
    "        )\n"
    "        modelo.fit(X_tr, y_tr)\n"
    "        y_prob = modelo.predict_proba(X_test)[:, 1]\n"
    "        auc = roc_auc_score(y_test, y_prob)\n\n"
    "        for t in thresholds:\n"
    "            y_pred = (y_prob >= t).astype(int)\n"
    "            cm = confusion_matrix(y_test, y_pred)\n"
    "            tn, fp, fn, tp = cm.ravel()\n"
    "            resultados_rf.append({\n"
    "                'Modelo': f'Random Forest (n={n_est})',\n"
    "                'Balanceo': nombre,\n"
    "                'Threshold': t,\n"
    "                'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,\n"
    "                'Precision': round(precision_score(y_test, y_pred, zero_division=0), 4),\n"
    "                'Recall':    round(recall_score(y_test, y_pred, zero_division=0), 4),\n"
    "                'F1':        round(f1_score(y_test, y_pred, zero_division=0), 4),\n"
    "                'ROC-AUC':   round(auc, 4)\n"
    "            })\n\n"
    "df_rf = pd.DataFrame(resultados_rf)\n"
    "print('\\n=== Resultados Random Forest ===')\n"
    "print(df_rf[['Modelo','Balanceo','Threshold','TP','FP','FN','Precision','Recall','F1','ROC-AUC']].to_string(index=False))"
)

# ============================================================
# FIX 9 — CatBoost: corregido segun literatura
# - Sin scale_pos_weight cuando se usa SMOTE (doble penalizacion)
# - Entrenar sobre los 3 datasets
# - 3 thresholds
# Ref: IJSDR2401084, ResearchGate 349156860
# ============================================================
catboost_md = md(
    "### **4.3. CatBoost**\n\n"
    "Con base en los resultados previos se seleccionaron los siguientes hiperparámetros, "
    "justificados por la literatura especializada:\n\n"
    "| Hiperparámetro | Valor | Justificación |\n"
    "|----------------|-------|---------------|\n"
    "| `iterations` | 300 | Balance entre capacidad de aprendizaje y tiempo de cómputo (ref. 2, 3) |\n"
    "| `learning_rate` | 0.05 | Tasa conservadora que evita sobreajuste en GBDT secuencial (ref. 43) |\n"
    "| `depth` | 6 | Profundidad óptima reportada para datos financieros desbalanceados (ref. 1) |\n"
    "| `eval_metric` | F1 | Métrica adecuada para clases desbalanceadas (ref. 2) |\n"
    "| `scale_pos_weight` | No aplicado | **Cuando se usa SMOTE el dataset ya está balanceado.** "
    "Aplicar ambos simultáneamente genera doble penalización que distorsiona el aprendizaje "
    "(IJSDR2401084, ResearchGate 349156860). Se entrena también sobre Under/Over para comparación. |\n\n"
    "> **Ventaja de CatBoost sobre RF:** Manejo nativo de variables categóricas mediante "
    "Ordered Target Encoding, arquitectura de Oblivious Trees para inferencia de baja latencia, "
    "y AUC reportado de 0.9837 en datasets financieros similares (ref. 1, 2, 3)."
)

catboost_code = code(
    "from catboost import CatBoostClassifier\n\n"
    "# CatBoost entrenado sobre los 3 datasets\n"
    "# SIN scale_pos_weight cuando el dataset ya esta balanceado (SMOTE/Over)\n"
    "# Ref: IJSDR2401084 — 'SMOTE y scale_pos_weight son estrategias alternativas'\n\n"
    "resultados_cb = []\n\n"
    "configs_cb = [\n"
    "    (X_under,       y_under,       'Undersampling'),\n"
    "    (X_train_over,  y_train_over,  'Oversampling'),\n"
    "    (X_train_smote, y_train_smote, 'SMOTE'),\n"
    "]\n\n"
    "for X_tr, y_tr, nombre in configs_cb:\n"
    "    print(f'Entrenando CatBoost | {nombre}...')\n"
    "    modelo_cat = CatBoostClassifier(\n"
    "        iterations=300,\n"
    "        learning_rate=0.05,\n"
    "        depth=6,\n"
    "        eval_metric='F1',\n"
    "        random_seed=42,\n"
    "        verbose=0\n"
    "    )\n"
    "    modelo_cat.fit(X_tr, y_tr)\n"
    "    y_prob = modelo_cat.predict_proba(X_test)[:, 1]\n"
    "    auc = roc_auc_score(y_test, y_prob)\n\n"
    "    for t in thresholds:\n"
    "        y_pred = (y_prob >= t).astype(int)\n"
    "        cm = confusion_matrix(y_test, y_pred)\n"
    "        tn, fp, fn, tp = cm.ravel()\n"
    "        resultados_cb.append({\n"
    "            'Modelo': 'CatBoost',\n"
    "            'Balanceo': nombre,\n"
    "            'Threshold': t,\n"
    "            'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,\n"
    "            'Precision': round(precision_score(y_test, y_pred, zero_division=0), 4),\n"
    "            'Recall':    round(recall_score(y_test, y_pred, zero_division=0), 4),\n"
    "            'F1':        round(f1_score(y_test, y_pred, zero_division=0), 4),\n"
    "            'ROC-AUC':   round(auc, 4)\n"
    "        })\n\n"
    "df_cb = pd.DataFrame(resultados_cb)\n"
    "print('\\n=== Resultados CatBoost ===')\n"
    "print(df_cb[['Balanceo','Threshold','TP','FP','FN','Precision','Recall','F1','ROC-AUC']].to_string(index=False))"
)

# ============================================================
# NUEVO — Punto 5: Ganancia Neta
# KPI central del taller. Ref: Cost-Sensitive Learning
# GN = TP*100 - FP*33
# Ref: Fraud Detection Handbook, arXiv 2005.02488, Leuven.AI
# ============================================================
gn_md = md(
    "## **5. Evaluación — KPI Ganancia Neta**\n\n"
    "La métrica de **Ganancia Neta** (Net Gain) es el KPI central del presente análisis. "
    "Se basa en el paradigma de **Aprendizaje Sensible al Costo** (*Cost-Sensitive Learning*), "
    "el cual establece que el costo de un falso negativo (fraude consumado) es asimétrico "
    "frente al costo de un falso positivo (cliente legítimo bloqueado).\n\n"
    "En el contexto de **Banco Falabella**, esta asimetría tiene consecuencias legales directas: "
    "un falso negativo activa el Art. 2341 del Código Civil (restitución obligatoria de fondos), "
    "mientras que un falso positivo activa el Art. 15 de la Constitución (vulneración del Hábeas Data).\n\n"
    "### Fórmula\n"
    "```\n"
    "Ganancia Neta = (TP × $I) - (FP × $C)\n"
    "Donde:\n"
    "  $I = 100  → ingreso por fraude correctamente detectado\n"
    "  $C = 33   → costo por falso positivo (cliente legítimo bloqueado)\n"
    "```\n\n"
    "**Referencia científica:** Fraud Detection Handbook (fraud-detection-handbook.github.io), "
    "arXiv 2005.02488 (Instance-Dependent Cost-Sensitive Learning), "
    "Leuven.AI — *Minimizing fraud losses using cost-sensitive ML*."
)

gn_code = code(
    "# ============================================================\n"
    "# PUNTO 5 — KPI Ganancia Neta\n"
    "# GN = TP*100 - FP*33\n"
    "# Ref: Fraud Detection Handbook, arXiv 2005.02488, Leuven.AI\n"
    "# ============================================================\n\n"
    "I = 100  # ingreso por TP\n"
    "C = 33   # costo por FP\n\n"
    "# Consolidar todos los resultados\n"
    "df_todos = pd.concat([df_lr, df_rf, df_cb], ignore_index=True)\n\n"
    "# Calcular Ganancia Neta\n"
    "df_todos['Ganancia_Neta'] = df_todos['TP'] * I - df_todos['FP'] * C\n\n"
    "# Tabla completa ordenada por Ganancia Neta\n"
    "df_gn = df_todos[['Modelo','Balanceo','Threshold','TP','FP','FN',\n"
    "                   'Recall','F1','ROC-AUC','Ganancia_Neta']]\\\n"
    "               .sort_values('Ganancia_Neta', ascending=False)\n\n"
    "print('=== TABLA COMPARATIVA COMPLETA — Ordenada por Ganancia Neta ===')\n"
    "print(df_gn.to_string(index=False))\n\n"
    "print('\\n=== MEJOR CONFIGURACION ===')\n"
    "mejor = df_gn.iloc[0]\n"
    "print(f'Modelo:        {mejor[\"Modelo\"]}')\n"
    "print(f'Balanceo:      {mejor[\"Balanceo\"]}')\n"
    "print(f'Threshold:     {mejor[\"Threshold\"]}')\n"
    "print(f'TP: {mejor[\"TP\"]} | FP: {mejor[\"FP\"]} | FN: {mejor[\"FN\"]}')\n"
    "print(f'Recall:        {mejor[\"Recall\"]}')\n"
    "print(f'F1:            {mejor[\"F1\"]}')\n"
    "print(f'ROC-AUC:       {mejor[\"ROC-AUC\"]}')\n"
    "print(f'Ganancia Neta: ${mejor[\"Ganancia_Neta\"]:,.0f}')"
)

gn_viz = code(
    "# Visualizacion — Ganancia Neta por modelo y configuracion\n\n"
    "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n\n"
    "# Grafico 1: Top 15 configuraciones\n"
    "top15 = df_gn.head(15).copy()\n"
    "top15['Config'] = top15['Modelo'].str[:12] + ' | ' + top15['Balanceo'] + ' | t=' + top15['Threshold'].astype(str)\n"
    "colores = ['gold' if i == 0 else 'steelblue' for i in range(len(top15))]\n"
    "axes[0].barh(top15['Config'][::-1], top15['Ganancia_Neta'][::-1], color=colores[::-1], edgecolor='black')\n"
    "axes[0].set_xlabel('Ganancia Neta ($)')\n"
    "axes[0].set_title('Top 15 configuraciones por Ganancia Neta')\n"
    "axes[0].axvline(0, color='red', linestyle='--', alpha=0.5)\n\n"
    "# Grafico 2: Ganancia Neta promedio por modelo\n"
    "gn_por_modelo = df_gn.groupby('Modelo')['Ganancia_Neta'].max().sort_values(ascending=True)\n"
    "colores2 = ['gold' if v == gn_por_modelo.max() else 'steelblue' for v in gn_por_modelo.values]\n"
    "axes[1].barh(gn_por_modelo.index, gn_por_modelo.values, color=colores2, edgecolor='black')\n"
    "axes[1].set_xlabel('Maxima Ganancia Neta ($)')\n"
    "axes[1].set_title('Maxima Ganancia Neta por tipo de modelo')\n\n"
    "plt.tight_layout()\n"
    "plt.show()"
)

gn_analisis = md(
    "### **Análisis de resultados — Ganancia Neta**\n\n"
    "El modelo con mayor Ganancia Neta representa la configuración óptima desde la perspectiva "
    "del negocio de **Banco Falabella**, equilibrando:\n\n"
    "1. **Maximizar TP:** Cada fraude detectado representa $100 de ingreso evitado y "
    "elimina la obligación de restitución bajo el Art. 2341 del Código Civil.\n\n"
    "2. **Minimizar FP:** Cada cliente legítimo bloqueado cuesta $33 en gestión administrativa "
    "y representa un riesgo de tutela bajo el Art. 15 de la Constitución.\n\n"
    "**Trade-off por threshold:**\n"
    "- **Threshold 0.2:** Maximiza Recall (detecta casi todo el fraude) pero genera más FP → "
    "mayor fricción operativa y riesgo legal por Hábeas Data.\n"
    "- **Threshold 0.5:** Equilibrio estándar.\n"
    "- **Threshold 0.78:** Minimiza FP (menos bloqueos a clientes legítimos) pero aumenta FN → "
    "mayor exposición al fraude consumado y obligaciones de restitución.\n\n"
    "> La Ganancia Neta es el único KPI que incorpora simultáneamente el costo del fraude "
    "no detectado y el costo de la fricción al cliente, reflejando la realidad operativa y "
    "legal de una entidad vigilada por la SFC como Banco Falabella.\n\n"
    "**Referencias:** arXiv 2005.02488, Fraud Detection Handbook cap.6, Leuven.AI (2022)."
)

# ============================================================
# ENSAMBLAR el notebook con los cambios
# Orden de insercion (de atras hacia adelante para no alterar indices):
# 1. Reemplazar celdas 76-82 con nueva seccion CatBoost + Ganancia Neta
# 2. Reemplazar celda 69 con LR tabla nueva
# 3. Insertar EDA balanceo despues de celda 62 (SMOTE)
# 4. Insertar doc_balanceo despues de celda 62
# 5. Insertar fix_scaler despues de celda 55 (split)
# ============================================================

# Paso 1: Reemplazar desde celda 75 hasta el final
# (75=md tabla RF, 76=codigo RF sin ejecutar, 77=md catboost, 78-82=catboost code)
nuevas_finales = [
    md("### **4.2. Random Forest — Tabla comparativa**"),
    rf_tabla_nueva,
    catboost_md,
    code("# Instalar catboost si no esta disponible\ntry:\n    from catboost import CatBoostClassifier\nexcept ImportError:\n    import subprocess\n    subprocess.run(['pip', 'install', 'catboost', '-q'])\n    from catboost import CatBoostClassifier"),
    catboost_code,
    gn_md,
    gn_code,
    gn_viz,
    gn_analisis,
]
cells = cells[:75] + nuevas_finales

# Paso 2: Reemplazar celda 69 (evaluar_modelo buggeada) con nueva funcion LR
# Celda 68 es md "tabla comparativa de resultados", celda 69 es la funcion con bug
cells[69] = lr_tabla_nueva

# Paso 3 y 4: Insertar documentacion y EDA despues de celda 62 (SMOTE)
cells = cells[:63] + [doc_balanceo, md("### **3.3. EDA Post-Balanceo**\n\nVerificación de la distribución de clases y estadísticas descriptivas tras cada técnica de balanceo.\nRequerido por el punto 3 del taller. Ref: MDPI 2078-2489."), eda_balanceo, eda_stats_balanceo] + cells[63:]

# Paso 5: Insertar escalado correcto despues del split
# Buscar celda del split (X_train, X_test, y_train, y_test = train_test_split...)
split_idx = None
for i, c in enumerate(cells):
    if 'train_test_split' in ''.join(c['source']) and c['cell_type'] == 'code':
        split_idx = i
        break
if split_idx:
    cells = cells[:split_idx+1] + [fix_scaler] + cells[split_idx+1:]

nb['cells'] = cells

with open(PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f'Notebook actualizado. Total celdas: {len(nb["cells"])}')
print('\nCambios aplicados:')
print('  [FIX 1] Scaler movido post-split (anti data leakage)')
print('  [FIX 2] isFlaggedFraud eliminada del pipeline')
print('  [FIX 3] Segundo scaler.fit_transform eliminado')
print('  [FIX 4] Escalado correcto insertado despues del split')
print('  [FIX 5] Documentacion tamanos datasets balanceados')
print('  [FIX 6] EDA post-balanceo (distribucion + histogramas)')
print('  [FIX 7] LR tabla con X_test fijo + ROC-AUC')
print('  [FIX 8] RF tabla completa (n=100/500, 3 datasets, 3 thresholds)')
print('  [FIX 9] CatBoost corregido (sin doble penalizacion, 3 datasets)')
print('  [NEW]   Punto 5 - Ganancia Neta completo')
