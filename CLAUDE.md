# CLAUDE.md — Deteccion de Fraude | Grupo 1
> Este archivo es la fuente de verdad para Claude en todas las sesiones de este proyecto.

---

## Contexto del Proyecto

**Tipo:** Evaluacion sumativa grupal academica
**Institucion:** Pontificia Universidad Javeriana — Especializacion en IA, Modulo 4
**Objetivo:** Aplicar metodologia CRISP-DM para detectar fraude en transacciones financieras
**Entidad financiera:** Banco Falabella (Colombia)
**Dataset:** PaySim — `data/PS_20174392719_1491204439457_log.csv`
- Target: `isFraud` (binario, desbalanceado: ~0.13% fraude)
- Columnas clave: `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`
- Columnas a eliminar: `nameOrig`, `nameDest`, `isFlaggedFraud`

---

## Estructura del Proyecto

```
deteccion_fraude_grupo_1/
├── CLAUDE.md                          ← este archivo
├── data/
│   └── PS_20174392719_1491204439457_log.csv
├── docs/
│   ├── entregables.md                 ← checklist oficial del taller
│   ├── plan_implementacion.md         ← plan tecnico detallado
│   ├── marco_teorico_resumen.md       ← resumen de la investigacion
│   └── investigacion_marco_teorico.pdf ← fuente original (98 refs)
├── notebooks/
│   ├── 01_eda.ipynb                   ← Punto 2 del taller
│   ├── 02_balanceo.ipynb              ← Punto 3 del taller
│   ├── 03_modelos.ipynb               ← Punto 4 del taller
│   └── 04_evaluacion_ganancia.ipynb   ← Punto 5 del taller
└── requirements.txt
```

---

## Reglas de Trabajo con Claude

### Siempre hacer
- Leer `docs/entregables.md` antes de empezar cualquier tarea nueva
- Leer `docs/plan_implementacion.md` para respetar el orden y estructura acordados
- Basar los argumentos teoricos en `docs/marco_teorico_resumen.md`
- Comentar el codigo con referencias al taller (ej: `# Punto 3 - SMOTE`)
- Mantener los notebooks limpios, con markdown explicativo en cada seccion

### Nunca hacer
- Cambiar el nombre de la columna target (`isFraud`)
- Aplicar SMOTE al conjunto de test (solo al train)
- Usar `accuracy` como metrica principal (el dataset es desbalanceado)
- Mezclar logica de entrenamiento y evaluacion en el mismo bloque de codigo

### Convenciones de codigo
- Variables: `snake_case`
- DataFrames: `df_original`, `df_under`, `df_over`, `df_smote`
- Modelos: `lr_model`, `rf_model`, `cb_model`
- Resultados: guardar en diccionarios para construir tabla comparativa final

---

## Entregables del Taller (resumen ejecutivo)

| # | Punto | Estado | Notebook |
|---|-------|--------|----------|
| 1 | Marco legal + Banco Falabella | Marco teorico listo, falta redaccion informe | — |
| 2 | EDA dataset original | Pendiente | `01_eda.ipynb` |
| 3 | 3 datasets balanceados + EDA | Pendiente | `02_balanceo.ipynb` |
| 4 | 3 modelos x 3 datasets | Pendiente | `03_modelos.ipynb` |
| 5 | KPI Ganancia Neta | Pendiente | `04_evaluacion_ganancia.ipynb` |
| 6 | Analisis etico Banco Falabella | Marco teorico listo, falta redaccion informe | — |

---

## KPI Principal: Ganancia Neta

```
GN = (TP × $I) - (FP × $C)
$I = 100   → ingreso por fraude correctamente detectado
$C = 33    → costo por falso positivo (cliente legitimo bloqueado)
```

Evaluar con thresholds: **0.2 | 0.5 | 0.78**

---

## Modelos a Implementar

### Regresion Logistica
- Thresholds: 0.2, 0.5, 0.78
- Parametros: `class_weight='balanced'`, `max_iter=1000`

### Random Forest
- `n_estimators`: 100 y 500
- `class_weight='balanced'`
- `bootstrap=True`
- `max_features='sqrt'`

### CatBoost
- Hiperparametros a justificar segun resultados previos
- Sugeridos inicialmente: `iterations=500`, `learning_rate=0.05`, `depth=6`, `auto_class_weights='Balanced'`

---

## Metricas a Registrar (por modelo x dataset x threshold)

- Matriz de confusion (TP, FP, TN, FN)
- Precision, Recall, F1-score (clase fraude)
- ROC-AUC
- **Ganancia Neta** (KPI principal)

---

## Fuentes Clave del Marco Teorico

Ver `docs/marco_teorico_resumen.md` para el resumen estructurado.
Fuente completa: `docs/investigacion_marco_teorico.pdf` (98 referencias)

Marco legal aplicable a Banco Falabella:
- Art. 246, 316, 323, 327 — Codigo Penal (Ley 599/2000)
- Art. 2341 — Codigo Civil (responsabilidad extracontractual)
- Art. 15 — Constitucion (Habeas Data)
- Ley 1266/2008 — Habeas Data Financiero
- Ley 1328/2009 — Proteccion consumidor financiero
- SARLAFT — Sistema de Administracion del Riesgo LA/FT
- Circulares SFC (Circular Externa 29/2014, actualizaciones 2024)
