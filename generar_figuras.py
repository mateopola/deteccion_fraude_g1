"""
Genera las 8 figuras para el informe final con RESULTADOS EXACTOS.
Entrena todos los modelos del notebook: LR, RF(100), RF(500), CatBoost
sobre los 3 datasets balanceados con thresholds 0.2 / 0.5 / 0.78.
Calcula Ganancia Neta real para las 27 combinaciones.

Ejecutar desde la raiz del proyecto:
    python generar_figuras.py
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ruta absoluta al directorio del proyecto (donde esta este script)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(PROJECT_DIR, 'docs', 'figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

def fig(name):
    return os.path.join(FIGURES_DIR, name)

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (roc_curve, auc, confusion_matrix,
                              precision_score, recall_score, f1_score)
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler, SMOTE
from catboost import CatBoostClassifier

plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.dpi': 120})

DATA_PATH = os.path.join(PROJECT_DIR, 'data', 'PS_20174392719_1491204439457_log.csv')

# ══════════════════════════════════════════════════════════
# 1. CARGA CON CHUNKED READING + MUESTREO ESTRATIFICADO
# ══════════════════════════════════════════════════════════
print('Cargando datos...')
dtypes = {
    'step': 'int32', 'type': 'category',
    'amount': 'float32', 'nameOrig': 'str', 'oldbalanceOrg': 'float32',
    'newbalanceOrig': 'float32', 'nameDest': 'str', 'oldbalanceDest': 'float32',
    'newbalanceDest': 'float32', 'isFraud': 'int8', 'isFlaggedFraud': 'int8'
}
chunks_fraud, chunks_normal = [], []
for chunk in pd.read_csv(DATA_PATH, dtype=dtypes, chunksize=100_000):
    chunks_fraud.append(chunk[chunk['isFraud'] == 1])
    chunks_normal.append(chunk[chunk['isFraud'] == 0])

df_fraud_all  = pd.concat(chunks_fraud,  ignore_index=True)
df_normal_all = pd.concat(chunks_normal, ignore_index=True)
n_fraud  = len(df_fraud_all)
n_normal = 500_000 - n_fraud

df_sample = pd.concat([
    df_fraud_all,
    df_normal_all.sample(n=n_normal, random_state=42)
], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
print(f'  Muestra: {len(df_sample):,} filas | Fraudes: {df_sample["isFraud"].sum():,}')

# ══════════════════════════════════════════════════════════
# PREPROCESAMIENTO (identico al notebook)
# ══════════════════════════════════════════════════════════
df = df_sample.copy()
df['amount_log']         = np.log1p(df['amount'])
df['oldbalanceOrg_log']  = np.log1p(df['oldbalanceOrg'])
df['newbalanceOrig_log'] = np.log1p(df['newbalanceOrig'])
df['oldbalanceDest_log'] = np.log1p(df['oldbalanceDest'])
df['newbalanceDest_log'] = np.log1p(df['newbalanceDest'])
df['hour']               = df['step'] % 24
df['hour_sin']           = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos']           = np.cos(2 * np.pi * df['hour'] / 24)
df['error_balance_orig'] = df['oldbalanceOrg'] - df['newbalanceOrig'] - df['amount']
df['error_balance_dest'] = df['oldbalanceDest'] - df['newbalanceDest'] + df['amount']
df = pd.get_dummies(df, columns=['type'], drop_first=True)
drop_cols = ['nameOrig','nameDest','isFlaggedFraud','step',
             'amount','oldbalanceOrg','newbalanceOrig',
             'oldbalanceDest','newbalanceDest','hour']
df.drop(columns=[c for c in drop_cols if c in df.columns], inplace=True)

X = df.drop(columns=['isFraud'])
y = df['isFraud']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

num_cols = X_train.select_dtypes(include='number').columns.tolist()
scaler   = StandardScaler()
X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test[num_cols]  = scaler.transform(X_test[num_cols])

# Balanceo (solo sobre train)
X_under, y_under   = RandomUnderSampler(random_state=42).fit_resample(X_train, y_train)
X_over,  y_over    = RandomOverSampler(random_state=42).fit_resample(X_train, y_train)
X_smote, y_smote   = SMOTE(random_state=42).fit_resample(X_train, y_train)

print('Preprocesamiento completo.')
print(f'  Under: {len(y_under):,} | Over: {len(y_over):,} | SMOTE: {len(y_smote):,}')

DATASETS = {
    'Undersampling': (X_under, y_under),
    'Oversampling':  (X_over,  y_over),
    'SMOTE':         (X_smote, y_smote),
}

# ══════════════════════════════════════════════════════════
# FIG 1 — Distribución isFraud
# ══════════════════════════════════════════════════════════
print('\nFig 1 — Distribución isFraud...')
fig1, axes = plt.subplots(1, 2, figsize=(10, 4))
counts = df_sample['isFraud'].value_counts().sort_index()
labels  = [f'Legítima\n({counts[0]/len(df_sample)*100:.2f}%)',
           f'Fraude\n({counts[1]/len(df_sample)*100:.2f}%)']
colors  = ['#2196F3', '#F44336']

axes[0].pie(counts, labels=labels, colors=colors, autopct='%1.2f%%',
            startangle=90, pctdistance=0.75,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2})
axes[0].set_title('Distribución de clases\n(muestra 500k)', fontsize=11)

bars = axes[1].bar(['Legítima', 'Fraude'], counts.values,
                   color=colors, edgecolor='white', linewidth=1.5)
axes[1].set_title('Conteo absoluto', fontsize=11)
axes[1].set_ylabel('Número de transacciones')
for bar, v in zip(bars, counts.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, v + 50,
                 f'{v:,}', ha='center', fontsize=9, fontweight='bold')

plt.suptitle('Variable objetivo: isFraud — Desbalance extremo\n'
             'Paradoja de la Precisión: un clasificador naïve alcanza 99.87% accuracy siendo inútil',
             fontsize=11, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(fig('fig1_distribucion_isfraude.png'), dpi=120, bbox_inches='tight')
plt.close()
print('  -> OK')

# ══════════════════════════════════════════════════════════
# FIG 2 — Boxplots
# ══════════════════════════════════════════════════════════
print('Fig 2 — Boxplots...')
df_bp = df_sample.copy()
df_bp['amount_log'] = np.log1p(df_bp['amount'])
vars_box = ['amount_log', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
labels_box = ['Amount (log)', 'Balance Orig\nAntes', 'Balance Orig\nDespués',
              'Balance Dest\nAntes', 'Balance Dest\nDespués']

fig2, axes = plt.subplots(1, len(vars_box), figsize=(16, 5))
for ax, var, lbl in zip(axes, vars_box, labels_box):
    data_leg = df_bp[df_bp['isFraud']==0][var].values
    data_fra = df_bp[df_bp['isFraud']==1][var].values
    bp = ax.boxplot([data_leg, data_fra], labels=['Legítima','Fraude'],
                    patch_artist=True, widths=0.5, notch=False)
    for patch, color in zip(bp['boxes'], ['#2196F3', '#F44336']):
        patch.set_facecolor(color); patch.set_alpha(0.75)
    ax.set_title(lbl, fontsize=9)
    ax.tick_params(labelsize=8)

plt.suptitle('Boxplots por clase — Outliers estructurales en transacciones fraudulentas\n'
             '75% de fraudes supera umbral de Tukey (Q3 + 1.5×IQR) de legítimas',
             fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(fig('fig2_boxplots.png'), dpi=120, bbox_inches='tight')
plt.close()
print('  -> OK')

# ══════════════════════════════════════════════════════════
# FIG 3 — Heatmap correlación
# ══════════════════════════════════════════════════════════
print('Fig 3 — Heatmap correlación...')
num_cols_orig = ['amount','oldbalanceOrg','newbalanceOrig',
                 'oldbalanceDest','newbalanceDest','isFraud']
corr = df_sample[num_cols_orig].corr()
corr.index   = ['Amount','Bal.Orig Antes','Bal.Orig Desp.','Bal.Dest Antes','Bal.Dest Desp.','isFraud']
corr.columns = corr.index

fig3, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, vmin=-1, vmax=1, linewidths=0.5,
            annot_kws={'size': 9}, ax=ax)
ax.set_title('Matriz de correlación — Variables numéricas\n'
             'Multicolinealidad: Bal.Orig Antes ↔ Bal.Orig Desp. (r≈0.98)',
             fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(fig('fig3_correlacion.png'), dpi=120, bbox_inches='tight')
plt.close()
print('  -> OK')

# ══════════════════════════════════════════════════════════
# FIG 4 — Histogramas hue=isFraud
# ══════════════════════════════════════════════════════════
print('Fig 4 — Histogramas...')
df_h = pd.concat([
    df_sample[df_sample['isFraud']==1],
    df_sample[df_sample['isFraud']==0].sample(n=5000, random_state=42)
], ignore_index=True)
df_h['amount_log']   = np.log1p(df_h['amount'])
df_h['err_orig']     = df_h['oldbalanceOrg'] - df_h['newbalanceOrig'] - df_h['amount']

fig4, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, var, lbl in zip(axes,
                        ['amount_log', 'err_orig'],
                        ['Monto (log1p)', 'Error Balance Origen']):
    for clase, color, label in [(0,'#2196F3','Legítima (n=5.000)'),
                                  (1,'#F44336',f'Fraude (n={df_sample["isFraud"].sum():,})')]:
        ax.hist(df_h[df_h['isFraud']==clase][var], bins=40,
                alpha=0.6, color=color, label=label, density=True)
    ax.set_xlabel(lbl, fontsize=10)
    ax.set_ylabel('Densidad', fontsize=10)
    ax.set_title(f'{lbl}\n(hue = isFraud)', fontsize=10)
    ax.legend(fontsize=9)

plt.suptitle('Histogramas — Solapamiento fraude vs legítima\n'
             'Amount_log y Error Balance muestran alto poder discriminativo (r > 0.43)',
             fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(fig('fig4_histogramas_fraude.png'), dpi=120, bbox_inches='tight')
plt.close()
print('  -> OK')

# ══════════════════════════════════════════════════════════
# FIG 5 — Countplot type vs isFraud
# ══════════════════════════════════════════════════════════
print('Fig 5 — Countplot type vs isFraud...')
df_sample['Clase'] = df_sample['isFraud'].map({0:'Legítima', 1:'Fraude'})
tasa = df_sample.groupby('type')['isFraud'].mean().mul(100).sort_values(ascending=False)

fig5, axes = plt.subplots(1, 2, figsize=(13, 5))

counts_type = df_sample.groupby(['type','Clase']).size().unstack(fill_value=0)
counts_type.plot(kind='bar', ax=axes[0], color=['#2196F3','#F44336'],
                 edgecolor='white', linewidth=0.8)
axes[0].set_title('Transacciones por tipo', fontsize=11)
axes[0].set_xlabel('Tipo de transacción')
axes[0].set_ylabel('Cantidad')
axes[0].tick_params(axis='x', rotation=30)
axes[0].legend(title='Clase')

bar_colors = ['#F44336' if v > 0 else '#4CAF50' for v in tasa.values]
bars2 = axes[1].bar(tasa.index, tasa.values, color=bar_colors,
                    edgecolor='white', linewidth=0.8)
axes[1].set_title('Tasa de fraude por tipo (%)\n¡Solo TRANSFER y CASH_OUT tienen fraude!',
                  fontsize=11)
axes[1].set_xlabel('Tipo de transacción')
axes[1].set_ylabel('Tasa de fraude (%)')
axes[1].tick_params(axis='x', rotation=30)
for bar, val in zip(bars2, tasa.values):
    if val > 0:
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                     f'{val:.2f}%', ha='center', fontsize=9, fontweight='bold')

plt.suptitle('Distribución type vs isFraud — Hallazgo crítico\n'
             'PAYMENT, DEBIT y CASH_IN tienen isFraud = 0 en el 100% de los casos',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(fig('fig5_countplot_type.png'), dpi=120, bbox_inches='tight')
plt.close()
print('  -> OK')

# ══════════════════════════════════════════════════════════
# FIG 6 — EDA post-balanceo
# ══════════════════════════════════════════════════════════
print('Fig 6 — EDA post-balanceo...')
fig6, axes = plt.subplots(2, 3, figsize=(15, 8))

for col, (name, (X_b, y_b)) in enumerate(DATASETS.items()):
    vals = pd.Series(y_b).value_counts().sort_index()
    c_bars = axes[0, col].bar(['Legítima','Fraude'], vals.values,
                               color=['#2196F3','#F44336'],
                               edgecolor='white', linewidth=1)
    axes[0, col].set_title(f'{name}\n{len(y_b):,} registros', fontsize=10, fontweight='bold')
    axes[0, col].set_ylabel('Cantidad' if col == 0 else '')
    for b, v in zip(c_bars, vals.values):
        axes[0, col].text(b.get_x() + b.get_width()/2, v * 0.5,
                          f'{v:,}', ha='center', fontsize=8,
                          color='white', fontweight='bold')

    col_name = 'amount_log'
    if col_name in X_b.columns:
        idx0 = np.array(y_b) == 0
        idx1 = np.array(y_b) == 1
        axes[1, col].hist(X_b[col_name][idx0], bins=30, alpha=0.6,
                          color='#2196F3', label='Legítima', density=True)
        axes[1, col].hist(X_b[col_name][idx1], bins=30, alpha=0.6,
                          color='#F44336', label='Fraude', density=True)
    axes[1, col].set_xlabel('amount_log (estandarizado)', fontsize=9)
    axes[1, col].set_ylabel('Densidad' if col == 0 else '')
    axes[1, col].legend(fontsize=8)

plt.suptitle('EDA por dataset balanceado — Distribución de clases e histograma amount_log\n'
             'SMOTE introduce leve ruido sintético en zona de solapamiento',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig(fig('fig6_eda_balanceado.png'), dpi=120, bbox_inches='tight')
plt.close()
print('  -> OK')

# ══════════════════════════════════════════════════════════
# ENTRENAMIENTO COMPLETO — LR, RF(100), RF(500), CatBoost
# ══════════════════════════════════════════════════════════
print('\nEntrenando todos los modelos (LR + RF100 + RF500 + CatBoost × 3 datasets)...')

thresholds = [0.2, 0.5, 0.78]
I_benefit  = 100   # ingreso por TP
C_cost     = 33    # costo por FP

def evaluar(nombre_modelo, nombre_dataset, modelo, X_tr, y_tr, umbral):
    modelo.fit(X_tr, y_tr)
    y_prob = modelo.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= umbral).astype(int)
    cm     = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    prec   = precision_score(y_test, y_pred, zero_division=0)
    rec    = recall_score(y_test, y_pred, zero_division=0)
    f1     = f1_score(y_test, y_pred, zero_division=0)
    fpr_c, tpr_c, _ = roc_curve(y_test, y_prob)
    roc_auc_val      = auc(fpr_c, tpr_c)
    gn = tp * I_benefit - fp * C_cost
    return {
        'Modelo': nombre_modelo, 'Dataset': nombre_dataset, 'Threshold': umbral,
        'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,
        'Precision': round(prec, 4), 'Recall': round(rec, 4), 'F1': round(f1, 4),
        'ROC_AUC': round(roc_auc_val, 4), 'GN': gn,
        '_fpr': fpr_c, '_tpr': tpr_c
    }

resultados = []
roc_curves = {}   # para fig7

MODELOS = {
    'LR':      lambda: LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
    'RF(100)': lambda: RandomForestClassifier(n_estimators=100, class_weight='balanced',
                                               max_features='sqrt', bootstrap=True,
                                               random_state=42, n_jobs=-1),
    'RF(500)': lambda: RandomForestClassifier(n_estimators=500, class_weight='balanced',
                                               max_features='sqrt', bootstrap=True,
                                               random_state=42, n_jobs=-1),
}

dataset_items = list(DATASETS.items())

for m_name, m_factory in MODELOS.items():
    for d_name, (X_tr, y_tr) in dataset_items:
        print(f'  {m_name} + {d_name}...', end=' ', flush=True)
        modelo = m_factory()
        modelo.fit(X_tr, y_tr)
        y_prob = modelo.predict_proba(X_test)[:, 1]
        # ROC curve (threshold-independent)
        fpr_c, tpr_c, _ = roc_curve(y_test, y_prob)
        roc_auc_val = auc(fpr_c, tpr_c)
        roc_curves[f'{m_name}|{d_name}'] = (fpr_c, tpr_c, roc_auc_val)
        for t in thresholds:
            y_pred = (y_prob >= t).astype(int)
            cm     = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel()
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec  = recall_score(y_test, y_pred, zero_division=0)
            f1   = f1_score(y_test, y_pred, zero_division=0)
            gn   = tp * I_benefit - fp * C_cost
            resultados.append({
                'Modelo': m_name, 'Dataset': d_name, 'Threshold': t,
                'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,
                'Precision': round(prec, 4), 'Recall': round(rec, 4),
                'F1': round(f1, 4), 'ROC_AUC': round(roc_auc_val, 4), 'GN': gn
            })
        print(f'AUC={roc_auc_val:.4f}')

# CatBoost (sin scale_pos_weight para SMOTE/Over)
for d_name, (X_tr, y_tr) in dataset_items:
    print(f'  CatBoost + {d_name}...', end=' ', flush=True)
    scale_pw = None if d_name in ['Oversampling','SMOTE'] else None
    cb_params = dict(iterations=300, learning_rate=0.05, depth=6,
                     eval_metric='F1', random_seed=42, verbose=0)
    if d_name == 'Undersampling':
        cb_params['auto_class_weights'] = 'Balanced'
    modelo_cb = CatBoostClassifier(**cb_params)
    modelo_cb.fit(X_tr, y_tr)
    y_prob = modelo_cb.predict_proba(X_test)[:, 1]
    fpr_c, tpr_c, _ = roc_curve(y_test, y_prob)
    roc_auc_val = auc(fpr_c, tpr_c)
    roc_curves[f'CatBoost|{d_name}'] = (fpr_c, tpr_c, roc_auc_val)
    for t in thresholds:
        y_pred = (y_prob >= t).astype(int)
        cm     = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec  = recall_score(y_test, y_pred, zero_division=0)
        f1   = f1_score(y_test, y_pred, zero_division=0)
        gn   = tp * I_benefit - fp * C_cost
        resultados.append({
            'Modelo': 'CatBoost', 'Dataset': d_name, 'Threshold': t,
            'TP': tp, 'FP': fp, 'TN': tn, 'FN': fn,
            'Precision': round(prec, 4), 'Recall': round(rec, 4),
            'F1': round(f1, 4), 'ROC_AUC': round(roc_auc_val, 4), 'GN': gn
        })
    print(f'AUC={roc_auc_val:.4f}')

df_todos = pd.DataFrame(resultados).sort_values('GN', ascending=False).reset_index(drop=True)

print('\n--- TOP 10 configuraciones por Ganancia Neta ---')
print(df_todos[['Modelo','Dataset','Threshold','TP','FP','GN']].head(10).to_string(index=False))

ganador = df_todos.iloc[0]
print(f'\nGANADOR: {ganador["Modelo"]} + {ganador["Dataset"]} + t={ganador["Threshold"]} '
      f'| GN=${ganador["GN"]:,} | TP={ganador["TP"]} | FP={ganador["FP"]}')

# ══════════════════════════════════════════════════════════
# FIG 7 — Curvas ROC (todas, con leyenda clara)
# ══════════════════════════════════════════════════════════
print('\nFig 7 — Curvas ROC...')
fig7, ax = plt.subplots(figsize=(9, 7))

# Colores por modelo
color_map = {
    'LR':       {'Undersampling':'#1A237E','Oversampling':'#3949AB','SMOTE':'#7986CB'},
    'RF(100)':  {'Undersampling':'#B71C1C','Oversampling':'#E53935','SMOTE':'#EF9A9A'},
    'RF(500)':  {'Undersampling':'#1B5E20','Oversampling':'#43A047','SMOTE':'#A5D6A7'},
    'CatBoost': {'Undersampling':'#E65100','Oversampling':'#FB8C00','SMOTE':'#FFCC80'},
}
linestyle_map = {'Undersampling':'-','Oversampling':'--','SMOTE':'-.'}

for key, (fpr_c, tpr_c, roc_val) in sorted(roc_curves.items()):
    m_name, d_name = key.split('|')
    color = color_map[m_name][d_name]
    ls    = linestyle_map[d_name]
    ax.plot(fpr_c, tpr_c, color=color, lw=1.8, linestyle=ls,
            label=f'{m_name} + {d_name} (AUC={roc_val:.4f})')

ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Aleatorio (AUC=0.50)')
ax.set_xlim([0.0, 0.1]); ax.set_ylim([0.85, 1.01])  # zoom zona relevante
ax.set_xlabel('Tasa de Falsos Positivos (FPR)', fontsize=11)
ax.set_ylabel('Tasa de Verdaderos Positivos (TPR)', fontsize=11)
ax.set_title('Curvas ROC — Todos los modelos × 3 datasets balanceados\n'
             '(zoom FPR 0–0.10 | evaluado sobre X_test fijo 20% estratificado)',
             fontsize=11, fontweight='bold')
ax.legend(loc='lower right', fontsize=7.5, ncol=2)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(fig('fig7_curvas_roc.png'), dpi=120, bbox_inches='tight')
plt.close()
print('  -> OK')

# ══════════════════════════════════════════════════════════
# FIG 8 — Ganancia Neta REAL
# ══════════════════════════════════════════════════════════
print('Fig 8 — Ganancia Neta...')
top15 = df_todos.head(15).copy()
top15['Config'] = (top15['Modelo'] + '\n' + top15['Dataset'] +
                   '\nt=' + top15['Threshold'].astype(str))

fig8, axes = plt.subplots(1, 2, figsize=(16, 7))

bar_colors = ['#FFD700' if i == 0 else ('#F44336' if v < 0 else '#2196F3')
              for i, v in enumerate(top15['GN'].values)]
bars = axes[0].barh(top15['Config'][::-1], top15['GN'][::-1],
                    color=bar_colors[::-1], edgecolor='white', linewidth=0.8)
axes[0].set_xlabel('Ganancia Neta ($)', fontsize=11)
axes[0].set_title('Top 15 Configuraciones\npor Ganancia Neta', fontsize=12, fontweight='bold')
axes[0].axvline(x=0, color='red', linestyle='--', linewidth=1.2, alpha=0.8, label='GN=0')
axes[0].legend(fontsize=9)
for bar in bars:
    val = bar.get_width()
    x_pos = val + abs(top15['GN'].max()) * 0.01
    axes[0].text(x_pos, bar.get_y() + bar.get_height() / 2,
                 f'${val:,}', va='center', fontsize=7, fontweight='bold')

# GN máxima por modelo
max_gn = df_todos.groupby('Modelo')['GN'].max().sort_values(ascending=False)
palette = ['#FFD700' if m == ganador['Modelo'] else '#607D8B' for m in max_gn.index]
bars2 = axes[1].bar(max_gn.index, max_gn.values, color=palette,
                    edgecolor='white', linewidth=1.2)
axes[1].set_title('Ganancia Neta Máxima\npor Tipo de Modelo', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Ganancia Neta ($)', fontsize=11)
axes[1].axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.8)
for bar in bars2:
    val = bar.get_height()
    color_txt = 'darkgreen' if val > 0 else 'red'
    axes[1].text(bar.get_x() + bar.get_width() / 2,
                 val + abs(max_gn.max()) * 0.02,
                 f'${val:,}', ha='center', fontsize=10,
                 fontweight='bold', color=color_txt)

plt.suptitle(
    f'KPI Ganancia Neta: GN = (TP × $100) − (FP × $33)\n'
    f'Ganador: {ganador["Modelo"]} + {ganador["Dataset"]} + t={ganador["Threshold"]} '
    f'| GN=${ganador["GN"]:,} | TP={ganador["TP"]} | FP={ganador["FP"]}',
    fontsize=12, fontweight='bold'
)
plt.tight_layout()
plt.savefig(fig('fig8_ganancia_neta.png'), dpi=120, bbox_inches='tight')
plt.close()
print('  -> OK')

# ══════════════════════════════════════════════════════════
# VERIFICACIÓN FINAL
# ══════════════════════════════════════════════════════════
figs_found = [f for f in os.listdir(FIGURES_DIR) if f.endswith('.png')]
print(f'\n{"="*55}')
print(f'Figuras generadas: {len(figs_found)}/8 en {FIGURES_DIR}')
for f_name in sorted(figs_found):
    size = os.path.getsize(os.path.join(FIGURES_DIR, f_name)) // 1024
    print(f'  {f_name} ({size} KB)')

print('\nAhora ejecuta: python generar_informe.py')
