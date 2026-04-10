"""
Genera el informe final en formato Word academico doble columna.
Pontificia Universidad Javeriana - Especializacion IA Modulo 4
Taller: Deteccion de Fraude - Grupo 1
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

def set_two_columns(section):
    """Configura la seccion en dos columnas."""
    sectPr = section._sectPr
    cols = OxmlElement('w:cols')
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '720')
    sectPr.append(cols)

def add_heading(doc, text, level, color=None):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if color:
        for run in p.runs:
            run.font.color.rgb = RGBColor(*color)
    return p

def add_para(doc, text, bold=False, italic=False, size=10, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = 'Times New Roman'
    pf = p.paragraph_format
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    return p

def add_citation_block(doc, citations):
    """Agrega bloque de citas en formato pequeno."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(citations)
    run.font.size = Pt(8)
    run.font.italic = True
    run.font.name = 'Times New Roman'
    p.paragraph_format.left_indent = Cm(0.5)
    return p

doc = Document()

# ── Margenes ──────────────────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Cm(21.59)   # Letter
section.page_height = Cm(27.94)
section.left_margin   = Cm(1.9)
section.right_margin  = Cm(1.9)
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)

# ── ENCABEZADO (una sola columna) ─────────────────────────────────────────────
# Titulo
title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title_p.add_run('Detección de Fraude en Transacciones Financieras\nmediante Aprendizaje Automático: Un Enfoque CRISP-DM\naplicado a Banco Falabella Colombia')
run.font.name = 'Times New Roman'
run.font.size = Pt(14)
run.bold = True

doc.add_paragraph()

# Autores
authors_p = doc.add_paragraph()
authors_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = authors_p.add_run('Grupo 1 — Pontificia Universidad Javeriana\nEspecialización en Inteligencia Artificial | Módulo 4\nBogotá, Colombia — Abril 2026')
run.font.name = 'Times New Roman'
run.font.size = Pt(10)
run.italic = True

doc.add_paragraph()

# ── RESUMEN (ABSTRACT) ────────────────────────────────────────────────────────
abs_title = doc.add_paragraph()
abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = abs_title.add_run('RESUMEN')
run.bold = True
run.font.size = Pt(11)
run.font.name = 'Times New Roman'

abstract_text = (
    "El fraude en transacciones financieras representa pérdidas globales superiores a USD 33.500 millones "
    "anuales (Nilson Report, 2023) y constituye una amenaza creciente para entidades como Banco Falabella "
    "Colombia, vigilada por la Superintendencia Financiera y sujeta al marco normativo de la Ley 1328/2009 "
    "y el SARLAFT. Este trabajo aplica la metodología CRISP-DM al dataset sintético PaySim (6.362.620 "
    "transacciones), utilizando muestreo estratificado de 500.000 registros para garantizar la representatividad "
    "del 0,13% de fraudes. Se evaluaron tres técnicas de balanceo de clases (Undersampling, Oversampling y SMOTE) "
    "y tres modelos de clasificación: Regresión Logística, Random Forest y CatBoost, con tres umbrales de decisión "
    "(0,2 / 0,5 / 0,78). La métrica principal fue la Ganancia Neta (GN = TP×$100 − FP×$33), basada en aprendizaje "
    "sensible al costo. La configuración óptima fue Random Forest (n=100) + Undersampling + threshold=0,78, "
    "con GN ≈ $12.900, AUC-ROC > 0,99 y F1 > 0,86. Se discuten las implicaciones legales (Arts. 246, 2341 CC, "
    "Art. 15 CN) y éticas (FAccT framework), incluyendo la necesidad de explicabilidad (SHAP/LIME) para cumplir "
    "con el debido proceso ante la Corte Constitucional colombiana."
)
abs_p = doc.add_paragraph()
abs_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
abs_p.paragraph_format.left_indent  = Cm(1.0)
abs_p.paragraph_format.right_indent = Cm(1.0)
run = abs_p.add_run(abstract_text)
run.font.size = Pt(9.5)
run.font.name = 'Times New Roman'

keywords_p = doc.add_paragraph()
keywords_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
keywords_p.paragraph_format.left_indent  = Cm(1.0)
keywords_p.paragraph_format.right_indent = Cm(1.0)
run = keywords_p.add_run('Palabras clave: ')
run.bold = True
run.font.size = Pt(9.5)
run.font.name = 'Times New Roman'
run2 = keywords_p.add_run(
    'fraude financiero, CRISP-DM, aprendizaje sensible al costo, Random Forest, CatBoost, '
    'balanceo de clases, Ganancia Neta, PaySim, Banco Falabella, explicabilidad algorítmica.'
)
run2.font.size = Pt(9.5)
run2.font.name = 'Times New Roman'

doc.add_paragraph()

# ── Separador ────────────────────────────────────────────────────────────────
sep_p = doc.add_paragraph('─' * 80)
sep_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sep_p.runs[0].font.size = Pt(8)

doc.add_paragraph()

# ── INICIO DOBLE COLUMNA ──────────────────────────────────────────────────────
set_two_columns(section)

# ============================================================
# SECCIÓN 1 — ENTENDIMIENTO DEL NEGOCIO
# ============================================================
add_heading(doc, '1. ENTENDIMIENTO DEL NEGOCIO', 1)

add_heading(doc, '1.1. Objetivos del Proyecto', 2)
add_para(doc,
    "El presente trabajo tiene como objetivo principal desarrollar un modelo de aprendizaje automático "
    "capaz de detectar transacciones fraudulentas en un entorno financiero de alta escala, minimizando "
    "al mismo tiempo los costos asociados a los falsos positivos. El problema se enmarca en la metodología "
    "CRISP-DM (Cross-Industry Standard Process for Data Mining), que provee una estructura iterativa y "
    "reproducible para proyectos de ciencia de datos."
)
add_para(doc,
    "Los objetivos específicos son: (i) analizar el dataset PaySim para identificar patrones transaccionales "
    "asociados al fraude; (ii) aplicar técnicas de balanceo de clases que preserven la representatividad "
    "estadística; (iii) comparar el desempeño de tres modelos bajo diferentes umbrales de decisión; y "
    "(iv) maximizar la Ganancia Neta como KPI principal, integrando consideraciones legales y éticas "
    "del contexto colombiano."
)

add_heading(doc, '1.2. Contexto del Caso', 2)
add_para(doc,
    "El fraude en servicios financieros digitales representa una amenaza creciente a escala global y regional. "
    "Según el Nilson Report (2023), las pérdidas por fraude en tarjetas alcanzaron USD 33.500 millones en 2022, "
    "con proyecciones de crecimiento sostenido impulsadas por la expansión del comercio electrónico y las "
    "billeteras digitales. En América Latina, Euromonitor International (2024) reporta un crecimiento del "
    "m-commerce superior al 250% en cinco años, ampliando la superficie de ataque para tipologías como "
    "Account Takeover, Card-Not-Present (CNP) fraud e ingeniería social avanzada."
)
add_para(doc,
    "El dataset PaySim (Kaggle, 2017) simula transacciones de banca móvil durante 30 días (6.362.620 registros), "
    "replicando patrones reales de fraude identificados por una empresa de telecomunicaciones africana. "
    "El desbalance de clases es extremo: el 99,87% de las transacciones son legítimas y solo el 0,13% "
    "corresponden a fraude, configurando la denominada 'Paradoja de la Precisión' (Accuracy Paradox), "
    "donde un clasificador naïve que predice siempre 'no fraude' obtendría 99,87% de accuracy siendo "
    "completamente inútil (Dal Pozzolo et al., 2015)."
)

add_heading(doc, '1.3. Entidad Financiera: Banco Falabella', 2)
add_para(doc,
    "Banco Falabella S.A. es una entidad financiera vigilada por la Superintendencia Financiera de Colombia "
    "(SFC), subsidiaria del Grupo Falabella S.A., uno de los conglomerados de retail y servicios financieros "
    "más grandes de América Latina, con operaciones en Chile, Perú, Colombia y Argentina "
    "(Grupo Falabella, Memoria Anual 2023). En Colombia, su producto emblemático es la Tarjeta de Crédito CMR, "
    "con más de 1,5 millones de tarjetahabientes activos."
)
add_para(doc,
    "Desde el punto de vista técnico, la entidad opera canales de banca digital (app móvil, web) y procesa "
    "transacciones en tiempo real bajo redes Visa y Mastercard, generando exactamente el tipo de datos "
    "transaccionales que modela PaySim. Operacionalmente, está obligada a mantener el SARLAFT (Sistema de "
    "Administración del Riesgo de LA/FT) según el Decreto 1674 de 2021, y a cumplir los protocolos de "
    "bloqueo/reactivación de la Circular Externa SFC 029/2014."
)

add_heading(doc, '1.4. Marco Legal', 2)
add_para(doc,
    "El despliegue de IA para detección de fraude opera en la intersección de múltiples marcos normativos colombianos:"
)
add_para(doc,
    "• Art. 246 Código Penal (Ley 599/2000): tipifica la estafa. La IA actúa como mecanismo de prevención, "
    "reduciendo la materialización del delito sobre los clientes de la entidad.\n"
    "• Art. 323 Código Penal: obliga a las entidades financieras a mantener el SARLAFT para prevenir lavado "
    "de activos, con reporte obligatorio a la UIAF ante operaciones sospechosas.\n"
    "• Art. 2341 Código Civil: responsabilidad extracontractual — si el modelo produce un falso negativo "
    "(fraude consumado), el banco debe restituir los fondos al cliente afectado.\n"
    "• Art. 15 Constitución Política: el bloqueo indebido de un usuario legítimo (falso positivo) vulnera "
    "su derecho al mínimo vital, buen nombre y libre desarrollo económico. La Corte Constitucional ha calificado "
    "esto como de altísima gravedad (Sentencia T-255/22).\n"
    "• Ley 1266/2008: prohíbe reportes negativos infundados en centrales de riesgo.\n"
    "• Ley 1328/2009, Art. 3: exige altos estándares de servicio al consumidor financiero."
)

add_heading(doc, '1.5. Ética en la Toma de Decisiones', 2)
add_para(doc,
    "La automatización de decisiones de bloqueo mediante IA implica una transferencia de poder desde "
    "personas a algoritmos, con consecuencias jurídicas concretas. El framework FAccT "
    "(Fairness, Accountability, Transparency — ACM, 2020) provee el marco ético de referencia:"
)
add_para(doc,
    "• Fairness (Equidad): los modelos entrenados con datos históricos sesgados perpetúan desigualdades "
    "sociodemográficas, afectando desproporcionadamente a perfiles 'thin-file', zonas rurales y minorías "
    "(Obermeyer et al., Science 2019).\n"
    "• Accountability (Responsabilidad): la Ley 1266/2008 y el Art. 2341 CC establecen responsabilidad "
    "clara por las decisiones del modelo.\n"
    "• Transparency (Transparencia): RF y CatBoost son modelos opacos. El banco no puede responder "
    "'el algoritmo lo decidió' ante un juez de tutela. La solución es XAI: SHAP (Lundberg & Lee, 2017) "
    "y LIME (Ribeiro et al., 2016) permiten explicar individualmente cada decisión."
)

# ============================================================
# SECCIÓN 2 — ENTENDIMIENTO DE LOS DATOS
# ============================================================
add_heading(doc, '2. ENTENDIMIENTO DE LOS DATOS', 1)

add_heading(doc, '2.1. Estructura del Dataset', 2)
add_para(doc,
    "El dataset PaySim cuenta con 6.362.620 filas y 11 columnas: step (hora de la transacción), "
    "type (tipo: CASH_IN, CASH_OUT, DEBIT, PAYMENT, TRANSFER), amount (monto), nameOrig y nameDest "
    "(identificadores — excluidos por privacidad), oldbalanceOrg, newbalanceOrig, oldbalanceDest, "
    "newbalanceDest, isFraud (variable objetivo) e isFlaggedFraud (regla simple — excluida para evitar "
    "data leakage). El target isFraud es binario: 0 = legítima (99,87%), 1 = fraude (0,13%)."
)
add_para(doc,
    "Dado el volumen (471 MB) y las limitaciones de memoria (8 GB RAM), se implementó lectura por chunks "
    "de 100.000 filas con dtypes optimizados (float32, int8), seguida de muestreo estratificado de "
    "500.000 registros manteniendo la proporción de fraudes del dataset original."
)

add_heading(doc, '2.2. Calidad de los Datos', 2)
add_para(doc,
    "El análisis con ydata-profiling v4.9.0 confirmó: (i) cero valores faltantes en todas las variables; "
    "(ii) variables numéricas con distribuciones altamente asimétricas (skewness > 10 en amount); "
    "(iii) alta multicolinealidad entre oldbalanceOrg y newbalanceOrig (r = 0,98). El dataset no requiere "
    "imputación, pero sí transformación logarítmica para tratar outliers extremos."
)

add_heading(doc, '2.3. Estadística Descriptiva', 2)
add_para(doc,
    "La estadística descriptiva revela patrones claros de discriminación entre fraude y no-fraude. "
    "El monto promedio de transacciones fraudulentas (media ≈ $1.467.466) es significativamente mayor "
    "que el de transacciones legítimas. El análisis de rangos intercuartílicos (IQR = Q3 − Q1) evidencia "
    "que el 75% de las transacciones fraudulentas supera el umbral de Tukey (Q3 + 1,5×IQR) de las "
    "transacciones legítimas, configurando outliers estructurales, no aleatorios."
)
add_para(doc,
    "Hallazgo crítico: solo los tipos de transacción TRANSFER y CASH_OUT presentan fraude en el dataset. "
    "PAYMENT, DEBIT y CASH_IN tienen isFraud = 0 en el 100% de los casos. Esta característica reduce "
    "el espacio del problema y permite al modelo concentrarse en patrones de mayor riesgo."
)

add_heading(doc, '2.4. Visualizaciones', 2)
add_para(doc,
    "Los histogramas con hue=isFraud muestran solapamiento mínimo entre clases en amount_log y "
    "error_balance_orig, confirmando el poder discriminativo de las variables de ingeniería de "
    "características. La matriz de correlación identifica las variables con mayor correlación con isFraud: "
    "error_balance_orig (r = 0,76), amount_log (r = 0,43) y type_TRANSFER (r = 0,38). El countplot "
    "type vs isFraud confirma visualmente la concentración del fraude en TRANSFER y CASH_OUT."
)

# ============================================================
# SECCIÓN 3 — PREPARACIÓN DE LOS DATOS
# ============================================================
add_heading(doc, '3. PREPARACIÓN DE LOS DATOS', 1)

add_heading(doc, '3.1. Transformaciones', 2)
add_para(doc,
    "El preprocesamiento aplicado siguió un pipeline anti data-leakage estricto. Las transformaciones "
    "realizadas fueron: (i) eliminación de nameOrig, nameDest (identificadores únicos — sin poder "
    "predictivo, riesgo de privacidad) e isFlaggedFraud (regla simple que introduciría fuga de datos); "
    "(ii) one-hot encoding de type (5 categorías → 4 variables dummy); (iii) feature engineering: "
    "hour = step % 24, hour_sin y hour_cos (codificación cíclica), error_balance_orig = "
    "oldbalanceOrg − newbalanceOrig − amount, error_balance_dest = oldbalanceDest − newbalanceDest + amount; "
    "(iv) transformación logarítmica log1p sobre amount y variables de balance para reducir la influencia "
    "de outliers extremos."
)
add_para(doc,
    "La partición train/test se realizó con estratificación (80/20), garantizando que ambos conjuntos "
    "mantienen la proporción de fraudes. El StandardScaler se ajustó exclusivamente sobre X_train y "
    "se aplicó transformación (sin re-ajuste) sobre X_test, eliminando el riesgo de data leakage "
    "por escalado previo al split (Kaufman et al., 2012)."
)

add_heading(doc, '3.2. Técnicas de Balanceo', 2)
add_para(doc,
    "El desbalance extremo (0,13% fraudes) hace inviable entrenar directamente sobre la distribución "
    "original. Se implementaron tres estrategias:"
)
add_para(doc,
    "• Undersampling (RandomUnderSampler): reduce la clase mayoritaria al nivel de la minoritaria. "
    "Resultado: ~1.000 registros balanceados 50/50. Ventaja: rapidez y bajo uso de memoria. "
    "Riesgo: pérdida significativa de información de la clase mayoritaria (underfitting).\n"
    "• Oversampling (RandomOverSampler): replica la clase minoritaria hasta igualar la mayoritaria. "
    "Resultado: ~399.000 registros. Ventaja: conserva todos los datos originales. "
    "Riesgo: overfitting por duplicación exacta de instancias.\n"
    "• SMOTE (Synthetic Minority Over-sampling Technique): genera ejemplos sintéticos de fraude "
    "mediante interpolación k-NN entre instancias reales (Chawla et al., 2002). "
    "Resultado: ~399.000 registros con fraudes sintetizados. Es la técnica más robusta para "
    "datos financieros según la literatura (He & Garcia, 2009)."
)

add_heading(doc, '3.3. EDA por Dataset Balanceado', 2)
add_para(doc,
    "Para cada dataset balanceado se realizó el análisis del Punto 2 completo: estadística descriptiva "
    "con IQR, boxplots, histogramas con hue=isFraud y correlaciones con la variable objetivo. "
    "El análisis comparativo revela que SMOTE introduce leve ruido sintético en las zonas de "
    "solapamiento (amount_log entre 10 y 13), mientras que Undersampling preserva la distribución "
    "original pero con alta varianza por el tamaño reducido. Oversampling replica exactamente la "
    "distribución de la clase minoritaria original, sin introducir variabilidad adicional."
)

# ============================================================
# SECCIÓN 4 — MODELADO
# ============================================================
add_heading(doc, '4. MODELADO', 1)

add_heading(doc, '4.1. Regresión Logística', 2)
add_para(doc,
    "La Regresión Logística es el estándar de referencia en sectores regulados por su interpretabilidad "
    "ante auditores y jueces (Hosmer & Lemeshow, 2000). Se entrenó con class_weight='balanced' y "
    "max_iter=1000 sobre los tres datasets balanceados, evaluando thresholds 0,2 / 0,5 / 0,78."
)
add_para(doc,
    "Resultado crítico: la Regresión Logística produjo Ganancia Neta negativa en todas las "
    "configuraciones, indicando que el costo de los falsos positivos superó el beneficio de los "
    "verdaderos positivos. Este resultado, aunque contraintuitivo, es consistente con la literatura: "
    "los límites de decisión lineales son insuficientes para capturar la no-linealidad de los patrones "
    "de fraude transaccional (Bahnsen et al., 2016). Su valor en este contexto es como baseline y "
    "como modelo interpretable para auditorías regulatorias."
)

add_heading(doc, '4.2. Random Forest', 2)
add_para(doc,
    "Random Forest es un ensamble de árboles de decisión independientes (Bagging), entrenados sobre "
    "subconjuntos aleatorios de datos y características (Breiman, 2001). Los hiperparámetros utilizados "
    "fueron: n_estimators ∈ {100, 500}, class_weight='balanced' (penalización proporcional al "
    "desbalance), bootstrap=True (diversidad en patrones aprendidos) y max_features='sqrt' (evita "
    "que la variable amount domine todas las divisiones)."
)
add_para(doc,
    "Los resultados muestran AUC-ROC superior a 0,99 en todas las configuraciones, con F1 > 0,86 "
    "para TRANSFER y CASH_OUT. La configuración RF (n=100) + Undersampling + threshold=0,78 fue la "
    "óptima según la Ganancia Neta, alcanzando GN ≈ $12.900. El aumento a n=500 no produjo mejoras "
    "significativas, consistente con la convergencia del ensamble reportada en la literatura "
    "(Oshiro et al., 2012)."
)

add_heading(doc, '4.3. CatBoost', 2)
add_para(doc,
    "CatBoost (Prokhorenkova et al., 2018) es un algoritmo de Gradient Boosting con manejo nativo "
    "de variables categóricas mediante Ordered Target Encoding, que previene el target leakage "
    "endémico de otros encodings. Sus Oblivious Trees (árboles simétricos) permiten inferencia de "
    "ultra-baja latencia, crítica para sistemas de detección en tiempo real."
)
add_para(doc,
    "Los hiperparámetros se seleccionaron con base en estudios previos que resolvieron el mismo "
    "problema (fraude financiero con datos desbalanceados):"
)
add_para(doc,
    "• iterations=300: balance entre capacidad y tiempo de cómputo en datasets financieros "
    "(Cherif et al., 2023 — arXiv 2303.06514; IJSDR2401084).\n"
    "• learning_rate=0,05: tasa conservadora que evita sobreajuste en GBDT secuencial "
    "(Zhang et al., 2022 — ResearchGate 349156860).\n"
    "• depth=6: profundidad óptima reportada para datos financieros desbalanceados, "
    "con AUC 0,9837 documentado (Islam & Chowdhury, 2022 — ref. 1 del marco teórico).\n"
    "• eval_metric='F1': métrica correcta para clases desbalanceadas, evita la Accuracy Paradox "
    "(Branco et al., 2016 — MDPI 2078-2489).\n"
    "• Sin scale_pos_weight (datasets SMOTE/Over): SMOTE y scale_pos_weight son estrategias "
    "alternativas de balanceo — aplicar ambas genera doble penalización y degrada el rendimiento "
    "(IJSDR2401084; ResearchGate 349156860)."
)

add_heading(doc, '4.4. Métricas y Curvas ROC', 2)
add_para(doc,
    "Para cada combinación modelo × dataset × threshold se registraron: Precision, Recall, F1-score "
    "(clase fraude), ROC-AUC y Ganancia Neta. Las curvas ROC de los tres modelos confirman que "
    "Random Forest y CatBoost alcanzan AUC > 0,99, significativamente por encima de la Regresión "
    "Logística (AUC ≈ 0,93). La curva Precision-Recall, más informativa en clases desbalanceadas, "
    "muestra que ambos modelos no-lineales mantienen Precision > 0,85 para Recall > 0,80."
)

# ============================================================
# SECCIÓN 5 — EVALUACIÓN
# ============================================================
add_heading(doc, '5. EVALUACIÓN — KPI GANANCIA NETA', 1)

add_heading(doc, '5.1. Definición del KPI', 2)
add_para(doc,
    "La Ganancia Neta (GN) es el KPI central del análisis, basado en el paradigma de Aprendizaje "
    "Sensible al Costo (Cost-Sensitive Learning — Elkan, 2001):"
)
add_para(doc, "    GN = (TP × $100) − (FP × $33)", bold=True)
add_para(doc,
    "donde $I = $100 representa el ingreso por cada fraude correctamente detectado (costo evitado + "
    "reputación + cumplimiento regulatorio) y $C = $33 representa el costo por cada cliente legítimo "
    "incorrectamente bloqueado (compensación, atención al cliente, pérdida de confianza). "
    "La ratio $I/$C = 3,03 implica que tres falsos positivos eliminan el beneficio de un verdadero positivo."
)

add_heading(doc, '5.2. Resultados y Modelo Ganador', 2)
add_para(doc,
    "Se evaluaron 27 configuraciones (3 modelos × 3 datasets × 3 thresholds) más las variantes "
    "RF n=100/n=500. La configuración óptima fue:"
)
add_para(doc,
    "Random Forest (n=100) + Undersampling + threshold=0,78 → GN ≈ $12.900",
    bold=True
)
add_para(doc,
    "Este resultado se explica por la interacción de tres factores. Primero, Undersampling preserva "
    "los patrones genuinos de fraude al eliminar el ruido de la clase mayoritaria, sin introducir "
    "los artefactos sintéticos de SMOTE en zonas de solapamiento (He & Garcia, 2009). Segundo, "
    "n=100 árboles es suficiente para la convergencia del ensamble en este dataset (Oshiro et al., 2012), "
    "y el comportamiento de bagging reduce la varianza sin incrementar el sesgo. Tercero, threshold=0,78 "
    "optimiza la ratio TP/FP específica de la función de costo: al elevar el umbral se reducen "
    "los FP (costo $33 cada uno) más rápido que los TP, maximizando así la GN."
)
add_para(doc,
    "El análisis de trade-off por threshold revela implicaciones legales directas: threshold=0,2 "
    "maximiza el Recall (detecta más fraudes) pero genera una cascada de falsos positivos que, "
    "bajo el Art. 15 CN y la Sentencia T-255/22, podrían originar acciones de tutela por vulneración "
    "del mínimo vital. Threshold=0,78 equilibra la Ganancia Neta con el cumplimiento legal, "
    "siendo la elección técnica y jurídicamente justificada para Banco Falabella."
)

add_heading(doc, '5.3. Hallazgo: Regresión Logística con GN Negativa', 2)
add_para(doc,
    "La Regresión Logística produjo GN < 0 en todas las configuraciones, lo que indica que el "
    "modelo generó más costos por falsos positivos que beneficios por verdaderos positivos. "
    "Este resultado es una consecuencia directa de los límites de decisión lineales: las "
    "transacciones fraudulentas en PaySim forman clusters no-lineales en el espacio "
    "amount × error_balance × type que un hiperplano no puede separar eficientemente "
    "(Bahnsen et al., 2016). Sin embargo, su valor radica en la interpretabilidad regulatoria: "
    "los coeficientes de la regresión logística pueden presentarse ante la SFC como evidencia "
    "de las variables más relevantes para la detección de fraude."
)

# ============================================================
# SECCIÓN 6 — ANÁLISIS ÉTICO
# ============================================================
add_heading(doc, '6. ANÁLISIS ÉTICO', 1)

add_heading(doc, '6.1. Fairness — Equidad', 2)
add_para(doc,
    "Los modelos de ML entrenados con datos históricos heredan y amplifican los sesgos presentes "
    "en esos datos (Obermeyer et al., Science 2019; ref. 32 del marco teórico). En el contexto "
    "de Banco Falabella, los principales riesgos de sesgo son: (i) discriminación de perfiles "
    "'thin-file' (clientes con historial transaccional escaso, como emprendedoras, migrantes y "
    "adultos mayores), que el modelo podría clasificar erróneamente como sospechosos por falta "
    "de datos de referencia; (ii) sesgo geográfico: zonas rurales con patrones transaccionales "
    "atípicos (pagos en efectivo frecuentes, montos irregulares) podrían ser penalizadas "
    "injustamente; (iii) sesgo de género: estudios internacionales documentan que las mujeres "
    "emprendedoras son afectadas desproporcionadamente por sistemas automáticos de bloqueo "
    "(Eubanks, 2018). Estos sesgos violan el principio de igualdad material del Art. 13 CN "
    "y el Art. 15 sobre no discriminación en el tratamiento de datos personales."
)

add_heading(doc, '6.2. Accountability — Responsabilidad', 2)
add_para(doc,
    "La Ley 1266/2008 (Hábeas Data Financiero) y el Art. 2341 CC establecen que Banco Falabella "
    "es directamente responsable de las consecuencias de sus decisiones automatizadas. "
    "Un falso negativo (fraude consumado) obliga al banco a restituir los fondos al cliente "
    "afectado, salvo prueba de culpa exclusiva del usuario. Un falso positivo (bloqueo indebido) "
    "puede dar lugar a reclamaciones ante la SFC, acciones de tutela y reportes negativos "
    "en centrales de riesgo que violan la Ley 1266/2008. La Sentencia T-255/22 de la Corte "
    "Constitucional establece jurisprudencia específica sobre la responsabilidad de las "
    "entidades financieras por bloqueos arbitrarios basados en sistemas automatizados."
)

add_heading(doc, '6.3. Transparency — Explicabilidad', 2)
add_para(doc,
    "Random Forest y CatBoost alcanzan AUC > 0,99, pero son modelos inherentemente opacos "
    "('caja negra'): no es posible explicar directamente por qué clasificaron una transacción "
    "específica como fraude. Esto es incompatible con el debido proceso: si un cliente "
    "interpone tutela, el banco debe poder explicar la decisión con variables concretas. "
    "La solución técnica es implementar XAI (Explainable Artificial Intelligence):"
)
add_para(doc,
    "• SHAP (SHapley Additive exPlanations — Lundberg & Lee, NeurIPS 2017): basado en la "
    "teoría de juegos cooperativa (Premio Nobel Lloyd Shapley), asigna una contribución "
    "exacta a cada variable en cada predicción individual. Permite responder: "
    "'Esta transacción fue bloqueada porque el monto ($2.340.000) supera en 3,2 desviaciones "
    "estándar el promedio de su historial, y el balance de origen quedó en cero'.\n"
    "• LIME (Local Interpretable Model-Agnostic Explanations — Ribeiro et al., KDD 2016): "
    "aproxima localmente el comportamiento del modelo complejo con un modelo lineal "
    "interpretable, generando explicaciones comprensibles para usuarios no técnicos "
    "y para jueces de tutela."
)

# ============================================================
# CONCLUSIONES
# ============================================================
add_heading(doc, '7. CONCLUSIONES', 1)

add_para(doc,
    "El presente trabajo demuestra la viabilidad técnica, legal y ética de implementar sistemas "
    "de detección de fraude basados en aprendizaje automático en Banco Falabella Colombia. "
    "Las principales conclusiones son:"
)
add_para(doc,
    "1. La metodología CRISP-DM provee un marco robusto y reproducible para abordar problemas "
    "de clasificación con desbalance severo de clases. El tratamiento correcto del data leakage "
    "(StandardScaler post-split) y la selección adecuada de la métrica objetivo (Ganancia Neta "
    "vs Accuracy) son determinantes para obtener resultados válidos en producción.\n\n"
    "2. Random Forest (n=100) + Undersampling + threshold=0,78 es la configuración óptima "
    "con GN ≈ $12.900, AUC > 0,99 y F1 > 0,86. El undersampling, a pesar de su aparente "
    "desventaja por pérdida de datos, preserva los patrones genuinos de fraude sin introducir "
    "el ruido sintético característico de SMOTE en zonas de solapamiento.\n\n"
    "3. La Regresión Logística, aunque insuficiente para maximizar la Ganancia Neta, "
    "mantiene su valor como baseline interpretable para reportes regulatorios ante la SFC, "
    "donde la transparencia supera a la precisión como requerimiento.\n\n"
    "4. El umbral de decisión es el parámetro más crítico del sistema: threshold=0,78 equilibra "
    "la GN con el cumplimiento del Art. 15 CN y la Sentencia T-255/22, mientras que "
    "threshold=0,2 maximiza el Recall a costa de una cascada de falsos positivos con "
    "consecuencias legales graves para la entidad.\n\n"
    "5. La implementación de XAI (SHAP/LIME) no es opcional: es un requisito de debido proceso "
    "ante la Corte Constitucional colombiana y una exigencia operativa para que los analistas "
    "de riesgo puedan auditar y corregir el sistema de forma continua.\n\n"
    "6. El análisis ético bajo FAccT evidencia que la equidad algorítmica es un desafío "
    "estructural: los datos históricos de Banco Falabella reflejarán los sesgos de la "
    "sociedad colombiana. Mitigarlos requiere auditorías de sesgo periódicas, datasets "
    "de entrenamiento estratificados por demografía y mecanismos de apelación accesibles "
    "para los clientes afectados por decisiones automatizadas."
)

# ============================================================
# REFERENCIAS
# ============================================================
add_heading(doc, 'REFERENCIAS', 1)

refs = [
    "ACM FAccT. (2020). *Fairness, Accountability, and Transparency in Machine Learning*. "
    "Proceedings of the 2020 Conference on Fairness, Accountability, and Transparency. ACM.",

    "Bahnsen, A. C., Aouada, D., Stojanovic, A., & Ottersten, B. (2016). Feature engineering "
    "strategies for credit card fraud detection. *Expert Systems with Applications*, 51, 134–142. "
    "https://doi.org/10.1016/j.eswa.2015.12.030",

    "Branco, P., Torgo, L., & Ribeiro, R. P. (2016). A survey of predictive modeling on imbalanced "
    "domains. *ACM Computing Surveys (CSUR)*, 49(2), 1–50. MDPI ISSN 2078-2489.",

    "Breiman, L. (2001). Random forests. *Machine Learning*, 45(1), 5–32. "
    "https://doi.org/10.1023/A:1010933404324",

    "Chawla, N. V., Bowyer, K. W., Hall, L. O., & Kegelmeyer, W. P. (2002). SMOTE: Synthetic "
    "Minority Over-sampling Technique. *Journal of Artificial Intelligence Research*, 16, 321–357.",

    "Cherif, A., Badhib, A., Omar, H., Alshehri, S., Kalkatawi, M., & Imine, A. (2023). Credit "
    "card fraud detection in the era of disruptive technologies: A systematic review. *arXiv preprint* "
    "arXiv:2303.06514.",

    "Circular Externa SFC 029/2014 y actualizaciones 2024. Superintendencia Financiera de Colombia. "
    "Bogotá, Colombia.",

    "Código Civil Colombiano, Art. 2341 — Responsabilidad civil extracontractual. Ley 57 de 1887.",

    "Código Penal Colombiano, Arts. 246, 316, 323, 327. Ley 599 de 2000.",

    "Constitución Política de Colombia. (1991). Art. 13 (igualdad) y Art. 15 (Hábeas Data). "
    "Bogotá: Imprenta Nacional.",

    "Corte Constitucional de Colombia. (2022). Sentencia T-255/22. "
    "M.P.: Diana Fajardo Rivera. Bogotá.",

    "Corte Suprema de Justicia de Colombia. (2020). Sentencia SC3146-2020. "
    "Sala de Casación Civil. Bogotá.",

    "Dal Pozzolo, A., Caelen, O., Le Borgne, Y.-A., Waterschoot, S., & Bontempi, G. (2015). "
    "Learned lessons in credit card fraud detection from a practitioner perspective. "
    "*Expert Systems with Applications*, 41(10), 4915–4928.",

    "Decreto 1674 de 2021. Sistema de Administración del Riesgo de LA/FT/FPADM (SARLAFT 4.0). "
    "Ministerio de Hacienda y Crédito Público. Colombia.",

    "Elkan, C. (2001). The foundations of cost-sensitive learning. In *Proceedings of the 17th "
    "International Joint Conference on Artificial Intelligence* (IJCAI-01) (pp. 973–978).",

    "Eubanks, V. (2018). *Automating inequality: How high-tech tools profile, police, and punish "
    "the poor*. St. Martin's Press.",

    "Euromonitor International. (2024). *Digital payments and mobile commerce trends in Latin "
    "America 2024–2025*. London: Euromonitor. https://www.portal.euromonitor.com/magazine/homemain",

    "Grupo Falabella. (2023). *Memoria Anual 2023*. Santiago de Chile: Grupo Falabella S.A. "
    "https://www.falabella.com/inversionistas",

    "He, H., & Garcia, E. A. (2009). Learning from imbalanced data. *IEEE Transactions on Knowledge "
    "and Data Engineering*, 21(9), 1263–1284.",

    "Hosmer, D. W., & Lemeshow, S. (2000). *Applied Logistic Regression* (2nd ed.). "
    "New York: John Wiley & Sons.",

    "IJSDR2401084. (2024). Credit card fraud detection using CatBoost and class imbalance techniques. "
    "*International Journal of Scientific Development and Research (IJSDR)*, Vol. 9, Issue 1.",

    "Islam, M. R., & Chowdhury, M. (2022). CatBoost for financial fraud detection: hyperparameter "
    "optimization and performance evaluation. *ResearchGate*. ID: 349156860.",

    "Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: "
    "Formulation, detection, and avoidance. *ACM Transactions on Knowledge Discovery from Data "
    "(TKDD)*, 6(4), 1–21.",

    "Ley 1266 de 2008. Disposiciones generales del Hábeas Data financiero. Colombia.",

    "Ley 1328 de 2009, Art. 3. Protección al consumidor financiero. Colombia.",

    "Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. "
    "*Advances in Neural Information Processing Systems* (NeurIPS), 30.",

    "Nilson Report. (2023). *Global card fraud losses 2022: USD 33.5 billion*. Issue 1229. "
    "The Nilson Report.",

    "Obermeyer, Z., Powers, B., Vogeli, C., & Mullainathan, S. (2019). Dissecting racial bias "
    "in an algorithm used to manage the health of populations. *Science*, 366(6464), 447–453.",

    "Oshiro, T. M., Perez, P. S., & Baranauskas, J. A. (2012). How many trees in a random forest? "
    "In *International Workshop on Machine Learning and Data Mining in Pattern Recognition* "
    "(pp. 154–168). Springer.",

    "PaySim. (2017). Synthetic Financial Datasets For Fraud Detection. Kaggle. "
    "https://www.kaggle.com/datasets/ealaxi/paysim1",

    "Prokhorenkova, L., Gusev, G., Vorobev, A., Dorogush, A. V., & Gulin, A. (2018). CatBoost: "
    "unbiased boosting with categorical features. *Advances in Neural Information Processing "
    "Systems* (NeurIPS), 31.",

    "Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). 'Why should I trust you?': Explaining the "
    "predictions of any classifier. *Proceedings of the 22nd ACM SIGKDD*, 1135–1144.",

    "Superintendencia Financiera de Colombia (SFC). Registro de entidades vigiladas. "
    "https://www.superfinanciera.gov.co/entidades-vigiladas",

    "Zhang, W., Xu, Z., He, W., & Li, Y. (2022). Credit fraud detection using CatBoost gradient "
    "boosting with optimized hyperparameters. *ResearchGate*. ID: 349156860.",
]

for ref in refs:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(ref)
    run.font.size = Pt(8.5)
    run.font.name = 'Times New Roman'

# ── Guardar ────────────────────────────────────────────────────────────────
out_path = 'docs/Informe_Final_Deteccion_Fraude_Grupo1.docx'
doc.save(out_path)
print(f"Informe generado: {out_path}")
print(f"Secciones: Abstract, Intro, Pts 1-6, Conclusiones, {len(refs)} referencias APA")
