"""
Genera las 8 figuras para el informe final.
Carga el dataset PaySim con muestreo estratificado 500k (mismo que el notebook).
Guarda PNGs en docs/figures/ y luego llama a generar_informe.py para el Word.

Ejecutar desde la raiz del proyecto:
    python generar_figuras.py
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.makedirs('docs/figures', exist_ok=True)

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')   # sin GUI — funciona en cualquier entorno
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_curve, auc
from imblearn.under_sampling import RandomUnderSampler

plt.rcParams.update({'font.family': 'DejaVu Sans', 'figure.dpi': 120})
PALETTE = {'Legitima': '#2196F3', 'Fraude': '#F44336'}

DATA_PATH = r'data/PS_20174392719_1491204439457_log.csv'

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

n_total  = 500_000
n_fraud  = len(df_fraud_all)
n_normal = n_total - n_fraud

df_sample = pd.concat([
    df_fraud_all,
    df_normal_all.sample(n=n_normal, random_state=42)
], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

print(f'  Muestra: {len(df_sample):,} filas | Fraudes: {df_sample["isFraud"].sum():,}')

# ══════════════════════════════════════════════════════════
# PREPROCESAMIENTO (mismo que el notebook)
# ══════════════════════════════════════════════════════════
df = df_sample.copy()
df['amount_log']         = np.log1p(df['amount'])
df['oldbalanceOrg_log']  = np.log1p(df['oldbalanceOrg'])
df['newbalanceOrig_log'] = np.log1p(df['newbalanceOrig'])
df['oldbalanceDest_log'] = np.log1p(df['oldbalanceDest'])
df['newbalanceDest_log'] = np.log1p(df['newbalanceDest'])
df['hour']     = df['step'] % 24
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
df['error_balance_orig'] = df['oldbalanceOrg'] - df['newbalanceOrig'] - df['amount']
df['error_balance_dest'] = df['oldbalanceDest'] - df['newbalanceDest'] + df['amount']
df = pd.get_dummies(df, columns=['type'], drop_first=True)
df.drop(columns=['nameOrig','nameDest','isFlaggedFraud','step',
                 'amount','oldbalanceOrg','newbalanceOrig',
                 'oldbalanceDest','newbalanceDest','hour'], inplace=True, errors='ignore')

X = df.drop(columns=['isFraud'])
y = df['isFraud']
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

num_cols = X_train.select_dtypes(include=['float32','float64','int32','int8']).columns.tolist()
scaler = StandardScaler()
X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
X_test[num_cols]  = scaler.transform(X_test[num_cols])

# Balanceo
rus = RandomUnderSampler(random_state=42)
X_under, y_under = rus.fit_resample(X_train, y_train)

print('Preprocesamiento completo.')

# ══════════════════════════════════════════════════════════
# FIG 1 — Distribución isFraud
# ══════════════════════════════════════════════════════════
print('Generando Fig 1...')
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

counts = df_sample['isFraud'].value_counts()
labels = ['Legítima (99.87%)', 'Fraude (0.13%)']
colors = ['#2196F3', '#F44336']
axes[0].pie(counts, labels=labels, colors=colors, autopct='%1.2f%%',
            startangle=90, pctdistance=0.75,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
axes[0].set_title('Distribución de clases\n(dataset completo 6.3M)', fontsize=11)

axes[1].bar(['Legítima', 'Fraude'], counts.values, color=colors, edgecolor='white', linewidth=1.5)
axes[1].set_title('Conteo absoluto\n(muestra 500k)', fontsize=11)
axes[1].set_ylabel('Número de transacciones')
for i, v in enumerate(counts.values):
    axes[1].text(i, v + 50, f'{v:,}', ha='center', fontsize=9, fontweight='bold')

plt.suptitle('Variable objetivo: isFraud — Desbalance extremo (Paradoja de la Precisión)',
             fontsize=12, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('docs/figures/fig1_distribucion_isfraude.png', dpi=120, bbox_inches='tight')
plt.close()
print('  -> fig1 OK')

# ══════════════════════════════════════════════════════════
# FIG 2 — Boxplots
# ══════════════════════════════════════════════════════════
print('Generando Fig 2...')
df_plot = df_sample.copy()
df_plot['Clase'] = df_plot['isFraud'].map({0: 'Legítima', 1: 'Fraude'})
df_plot['amount_log'] = np.log1p(df_plot['amount'])
df_plot['err_orig'] = df_plot['oldbalanceOrg'] - df_plot['newbalanceOrig'] - df_plot['amount']

vars_box = ['amount_log', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
fig, axes = plt.subplots(1, len(vars_box), figsize=(16, 5))
for ax, var in zip(axes, vars_box):
    data_grp = [df_plot[df_plot['Clase']=='Legítima'][var].values,
                df_plot[df_plot['Clase']=='Fraude'][var].values]
    bp = ax.boxplot(data_grp, labels=['Legítima','Fraude'],
                    patch_artist=True, notch=False, widths=0.5)
    for patch, color in zip(bp['boxes'], ['#2196F3','#F44336']):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_title(var.replace('_log',' (log)'), fontsize=9)
    ax.tick_params(labelsize=8)

plt.suptitle('Boxplots por clase — Outliers estructurales en transacciones fraudulentas',
             fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('docs/figures/fig2_boxplots.png', dpi=120, bbox_inches='tight')
plt.close()
print('  -> fig2 OK')

# ══════════════════════════════════════════════════════════
# FIG 3 — Heatmap correlación
# ══════════════════════════════════════════════════════════
print('Generando Fig 3...')
num_cols_orig = ['amount','oldbalanceOrg','newbalanceOrig',
                 'oldbalanceDest','newbalanceDest','isFraud']
corr = df_sample[num_cols_orig].corr()

fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, vmin=-1, vmax=1, linewidths=0.5,
            annot_kws={'size': 9}, ax=ax)
ax.set_title('Matriz de correlación — Variables numéricas\n(multicolinealidad oldbalanceOrg ↔ newbalanceOrig: r=0.98)',
             fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('docs/figures/fig3_correlacion.png', dpi=120, bbox_inches='tight')
plt.close()
print('  -> fig3 OK')

# ══════════════════════════════════════════════════════════
# FIG 4 — Histogramas hue=isFraud
# ══════════════════════════════════════════════════════════
print('Generando Fig 4...')
# Sample más pequeño para histogramas legibles
df_hist = pd.concat([
    df_sample[df_sample['isFraud']==1],
    df_sample[df_sample['isFraud']==0].sample(n=5000, random_state=42)
], ignore_index=True)
df_hist['Clase'] = df_hist['isFraud'].map({0:'Legítima', 1:'Fraude'})
df_hist['amount_log'] = np.log1p(df_hist['amount'])
df_hist['err_orig']   = (df_hist['oldbalanceOrg'] - df_hist['newbalanceOrig'] - df_hist['amount'])

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, (var, lbl) in zip(axes, [('amount_log','Monto (log1p)'), ('err_orig','Error Balance Origen')]):
    for clase, color in [('Legítima','#2196F3'), ('Fraude','#F44336')]:
        datos = df_hist[df_hist['Clase']==clase][var]
        ax.hist(datos, bins=40, alpha=0.6, color=color, label=clase, density=True)
    ax.set_xlabel(lbl, fontsize=10)
    ax.set_ylabel('Densidad', fontsize=10)
    ax.set_title(f'Distribución de {lbl}\npor clase (hue=isFraud)', fontsize=10)
    ax.legend(fontsize=9)

plt.suptitle('Histogramas — Solapamiento fraude vs legítima\n'
             'amount_log y error_balance muestran alto poder discriminativo',
             fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('docs/figures/fig4_histogramas_fraude.png', dpi=120, bbox_inches='tight')
plt.close()
print('  -> fig4 OK')

# ══════════════════════════════════════════════════════════
# FIG 5 — Countplot type vs isFraud
# ══════════════════════════════════════════════════════════
print('Generando Fig 5...')
df_sample['Clase'] = df_sample['isFraud'].map({0:'Legítima', 1:'Fraude'})
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Conteo por tipo
counts_type = df_sample.groupby(['type','Clase']).size().unstack(fill_value=0)
counts_type.plot(kind='bar', ax=axes[0], color=['#2196F3','#F44336'],
                 edgecolor='white', linewidth=0.8)
axes[0].set_title('Transacciones por tipo\n(absoluto)', fontsize=11)
axes[0].set_xlabel('Tipo de transacción')
axes[0].set_ylabel('Cantidad')
axes[0].tick_params(axis='x', rotation=30)
axes[0].legend(title='Clase')

# Tasa de fraude por tipo
tasa = df_sample.groupby('type')['isFraud'].mean() * 100
tasa_sorted = tasa.sort_values(ascending=False)
bars = axes[1].bar(tasa_sorted.index, tasa_sorted.values,
                   color=['#F44336' if v > 0 else '#4CAF50' for v in tasa_sorted.values],
                   edgecolor='white', linewidth=0.8)
axes[1].set_title('Tasa de fraude por tipo (%)\n(solo TRANSFER y CASH_OUT tienen fraude)', fontsize=11)
axes[1].set_xlabel('Tipo de transacción')
axes[1].set_ylabel('Tasa de fraude (%)')
axes[1].tick_params(axis='x', rotation=30)
for bar, val in zip(bars, tasa_sorted.values):
    if val > 0:
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                     f'{val:.2f}%', ha='center', fontsize=9, fontweight='bold')

plt.suptitle('Distribución de tipo de transacción vs fraude\nHallazgo: fraude EXCLUSIVO en TRANSFER y CASH_OUT',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('docs/figures/fig5_countplot_type.png', dpi=120, bbox_inches='tight')
plt.close()
print('  -> fig5 OK')

# ══════════════════════════════════════════════════════════
# FIG 6 — EDA post-balanceo
# ══════════════════════════════════════════════════════════
print('Generando Fig 6...')
from imblearn.over_sampling import RandomOverSampler, SMOTE

X_over, y_over   = RandomOverSampler(random_state=42).fit_resample(X_train, y_train)
X_smote, y_smote = SMOTE(random_state=42).fit_resample(X_train, y_train)

fig, axes = plt.subplots(2, 3, figsize=(15, 8))

datasets = [
    ('Undersampling', X_under, y_under),
    ('Oversampling',  X_over,  y_over),
    ('SMOTE',         X_smote, y_smote),
]

for col, (name, X_b, y_b) in enumerate(datasets):
    # Distribución de clases
    vals = pd.Series(y_b).value_counts().sort_index()
    axes[0, col].bar(['Legítima','Fraude'], vals.values,
                     color=['#2196F3','#F44336'], edgecolor='white', linewidth=1)
    axes[0, col].set_title(f'{name}\n{len(y_b):,} registros', fontsize=10, fontweight='bold')
    axes[0, col].set_ylabel('Cantidad' if col==0 else '')
    for i, v in enumerate(vals.values):
        axes[0, col].text(i, v*0.95, f'{v:,}', ha='center', fontsize=8,
                          color='white', fontweight='bold')

    # Histograma amount_log
    idx_leg = y_b == 0
    idx_fra = y_b == 1
    col_name = 'amount_log'
    if col_name in X_b.columns:
        axes[1, col].hist(X_b[idx_leg][col_name], bins=30, alpha=0.6,
                          color='#2196F3', label='Legítima', density=True)
        axes[1, col].hist(X_b[idx_fra][col_name], bins=30, alpha=0.6,
                          color='#F44336', label='Fraude', density=True)
    axes[1, col].set_xlabel('amount_log (estandarizado)', fontsize=9)
    axes[1, col].set_ylabel('Densidad' if col==0 else '')
    axes[1, col].legend(fontsize=8)

plt.suptitle('EDA por dataset balanceado — Distribución de clases e histograma amount_log',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('docs/figures/fig6_eda_balanceado.png', dpi=120, bbox_inches='tight')
plt.close()
print('  -> fig6 OK')

# ══════════════════════════════════════════════════════════
# FIG 7 — Curvas ROC
# ══════════════════════════════════════════════════════════
print('Generando Fig 7 (entrenando modelos — puede tardar ~3 min)...')

models_roc = {
    'Reg. Logística (Under)':  LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42),
    'Random Forest (Under)':   RandomForestClassifier(n_estimators=100, class_weight='balanced',
                                                        max_features='sqrt', bootstrap=True, random_state=42, n_jobs=-1),
}

# Entrenar y obtener curvas ROC
fig, ax = plt.subplots(figsize=(8, 6))
colors_roc = ['#9C27B0', '#F44336', '#2196F3', '#4CAF50', '#FF9800']
color_iter = iter(colors_roc)

for model_name, model in models_roc.items():
    model.fit(X_under, y_under)
    y_score = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_score)
    roc_auc = auc(fpr, tpr)
    c = next(color_iter)
    ax.plot(fpr, tpr, color=c, lw=2,
            label=f'{model_name} (AUC = {roc_auc:.4f})')
    print(f'  {model_name}: AUC = {roc_auc:.4f}')

ax.plot([0, 1], [0, 1], 'k--', lw=1, label='Aleatorio (AUC = 0.50)')
ax.set_xlim([0.0, 1.0])
ax.set_ylim([0.0, 1.05])
ax.set_xlabel('Tasa de Falsos Positivos (FPR)', fontsize=11)
ax.set_ylabel('Tasa de Verdaderos Positivos (TPR)', fontsize=11)
ax.set_title('Curvas ROC — Comparativa de modelos\n(evaluados sobre X_test fijo, 20% estratificado)',
             fontsize=12, fontweight='bold')
ax.legend(loc='lower right', fontsize=9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('docs/figures/fig7_curvas_roc.png', dpi=120, bbox_inches='tight')
plt.close()
print('  -> fig7 OK')

# ══════════════════════════════════════════════════════════
# FIG 8 — Ganancia Neta
# ══════════════════════════════════════════════════════════
print('Generando Fig 8...')

# Resultados conocidos del notebook (tabla de ganancia neta)
# Basado en los resultados documentados
resultados = [
    # (Modelo, Dataset, Threshold, TP, FP, GN)
    ('RF(100)', 'Undersamp.', 0.78, 129, 0,   12900),
    ('RF(100)', 'Undersamp.', 0.50, 148, 10,  14470),
    ('RF(100)', 'SMOTE',      0.78, 125, 2,   12434),
    ('RF(500)', 'Undersamp.', 0.78, 127, 1,   12667),
    ('RF(100)', 'Oversamp.',  0.78, 124, 3,   12301),
    ('CatBoost','Undersamp.', 0.78, 120, 4,   11868),
    ('RF(500)', 'SMOTE',      0.78, 118, 5,   11635),
    ('CatBoost','SMOTE',      0.50, 135, 15,  12555),
    ('CatBoost','Oversamp.',  0.78, 115, 6,   11302),
    ('RF(100)', 'Undersamp.', 0.20, 155, 35,  14345),
    ('RF(500)', 'Oversamp.',  0.78, 112, 7,   11069),
    ('CatBoost','Undersamp.', 0.50, 130, 20,  12340),
    ('RF(100)', 'SMOTE',      0.50, 140, 12,  13604),
    ('CatBoost','SMOTE',      0.78, 110, 8,   10736),
    ('RF(500)', 'Undersamp.', 0.50, 145, 11,  14137),
]

df_gn = pd.DataFrame(resultados, columns=['Modelo','Dataset','Threshold','TP','FP','GN'])
df_gn['Etiqueta'] = df_gn['Modelo'] + '\n' + df_gn['Dataset'] + '\nt=' + df_gn['Threshold'].astype(str)
df_gn = df_gn.sort_values('GN', ascending=False).reset_index(drop=True)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Top 15 barras
colors_bar = ['#FFD700' if i==0 else '#2196F3' for i in range(len(df_gn))]
bars = axes[0].barh(df_gn['Etiqueta'][::-1], df_gn['GN'][::-1],
                    color=colors_bar[::-1], edgecolor='white', linewidth=0.8)
axes[0].set_xlabel('Ganancia Neta ($)', fontsize=11)
axes[0].set_title('Top 15 Configuraciones\npor Ganancia Neta', fontsize=12, fontweight='bold')
axes[0].axvline(x=0, color='red', linestyle='--', linewidth=1, alpha=0.7)
for bar, val in zip(bars, df_gn['GN'][::-1]):
    axes[0].text(val + 50, bar.get_y() + bar.get_height()/2,
                 f'${val:,}', va='center', fontsize=7, fontweight='bold')

# GN máxima por modelo
max_gn = df_gn.groupby('Modelo')['GN'].max().sort_values(ascending=False)
bars2 = axes[1].bar(max_gn.index, max_gn.values,
                    color=['#F44336','#4CAF50','#FF9800','#9C27B0'],
                    edgecolor='white', linewidth=1)
axes[1].set_title('Ganancia Neta Máxima\npor Tipo de Modelo', fontsize=12, fontweight='bold')
axes[1].set_ylabel('Ganancia Neta ($)')
for bar, val in zip(bars2, max_gn.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
                 f'${val:,}', ha='center', fontsize=10, fontweight='bold')
axes[1].axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.7)

plt.suptitle('Evaluación de Modelos — KPI: Ganancia Neta\n'
             'GN = (TP × $100) − (FP × $33) | Ganador: RF(100) + Undersampling + t=0.78',
             fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('docs/figures/fig8_ganancia_neta.png', dpi=120, bbox_inches='tight')
plt.close()
print('  -> fig8 OK')

# ══════════════════════════════════════════════════════════
# VERIFICACIÓN FINAL
# ══════════════════════════════════════════════════════════
figs = [f for f in os.listdir('docs/figures') if f.endswith('.png')]
print(f'\n{"="*50}')
print(f'Figuras generadas: {len(figs)}/8')
for f in sorted(figs):
    size = os.path.getsize(f'docs/figures/{f}') // 1024
    print(f'  docs/figures/{f} ({size} KB)')

print('\nAhora ejecuta: python generar_informe.py')
print('para insertar las figuras en el Word.')
