# Resumen Marco Teorico — Deteccion de Fraude
> Extraido de: `investigacion_marco_teorico.pdf` (98 referencias)
> Usar como fuente de informacion para redactar el informe del taller.

---

## 1. Marco Legal Colombiano

### Codigo Penal (Ley 599 de 2000)
| Articulo | Delito | Aplicacion al proyecto |
|----------|--------|----------------------|
| Art. 246 | Estafa | Uso de IA para detectar transacciones fraudulentas |
| Art. 316 | Captacion masiva y habitual de dineros | Obliga a entidades a tener controles de monitoreo |
| Art. 323 | Lavado de activos | SARLAFT como sistema obligatorio |
| Art. 327 | Enriquecimiento ilicito de particulares | Responsabilidad penal por omision de controles |

> **Posicion de garante:** La omision de controles antifraude no es un fallo tecnico, es una infraccion penal. La automatizacion con IA es un escudo legal indispensable.

### Codigo Civil
- **Art. 2341** — Responsabilidad civil extracontractual: si el modelo de IA tiene un falso negativo (fraude consumado), el banco debe restituir los fondos al cliente. La excepcion solo aplica si se prueba culpa exclusiva del usuario.

### Constitucion Politica
- **Art. 15** — Habeas Data: bloquear fondos de un usuario legitimo (falso positivo) vulnera su derecho al minimo vital, buen nombre y libre desarrollo economico. La Corte Constitucional ha calificado esto como de altisima gravedad (Sentencia T-255/22).

### Leyes complementarias
- **Ley 1266/2008** — Habeas Data Financiero: principios de veracidad, necesidad y circulacion restringida de datos personales. Prohibe reportes negativos infundados en centrales de riesgo.
- **Ley 1328/2009 Art. 3** — Debida diligencia: las entidades deben prestar servicio con altos estandares, priorizando la atencion al consumidor financiero.
- **SARLAFT** — Sistema de Administracion del Riesgo de LA/FT: obliga a reportar operaciones sospechosas a la UIAF.
- **Circular Externa SFC 29/2014 y actualizaciones 2024** — Autoriza bloqueos preventivos, pero exige procedimiento expedito de reactivacion.

---

## 2. Debido Proceso Institucional (3 Dimensiones)

### Dimension Tecnica
- El modelo debe tener umbral de decision (threshold) dinamico y matematicamente justificado
- Prohibido usar antecedentes historicos como unico criterio de bloqueo (Corte Constitucional)
- Aplica directamente a la seleccion de threshold: 0.2 / 0.5 / 0.78 del taller

### Dimension Operacional
- El bloqueo debe generar notificacion al cliente en tiempo real (SMS, email, app)
- Debe ofrecer validacion multifactorial para reactivacion rapida
- La carga probatoria no debe recaer sobre el ciudadano

### Dimension Legal y Jurisdiccional
- Los bancos no son entes judiciales — no pueden bloquear indefinidamente
- Bloqueos prolongados activan Accion de Tutela (derechos inalienables)
- Reportes obligatorios a UIAF si el bloqueo se sostiene por sospecha fundada

---

## 3. Contexto Operacional y Estrategico

### Ecosistema de pagos en America Latina
- Tendencia dominante: sociedades sin efectivo (cashless societies) — Euromonitor 2024-2025
- M-commerce y billeteras digitales: crecimiento proyectado >250% en 5 anos
- Tipologias de fraude evolucionaron: Account Takeover, ingenieria social, CNP fraud
- Perdidas globales por fraude en tarjetas: >33.5 mil millones USD/ano

### El dilema costo-beneficio
- **Maximizar Recall** (detectar todo el fraude) → cascada de falsos positivos → churn del cliente
- **43%** de instituciones reportan aumento de FP al desplegar modelos no calibrados
- **58%** de empresas reportan aumento de abandono de clientes por controles agresivos
- Solucion: optimizar **Ganancia Neta** en lugar de Accuracy o Recall aislados

### Formula KPI Ganancia Neta
```
GN = (TP × $100) - (FP × $33)
```
Basado en Cost-Sensitive Learning (Aprendizaje Sensible al Costo)

---

## 4. Justificacion Cientifica de los Modelos

### Problema de desbalance de clases
- Fraudes = ~0.13% del dataset → "Paradoja de la precision" (Accuracy Paradox)
- Un modelo que predice siempre "no fraude" tiene ~99.87% accuracy pero es inutil

### Comparativa de tecnicas de balanceo

| Tecnica | Ventaja | Riesgo |
|---------|---------|--------|
| **Undersampling** | Rapido, menos memoria | Pierde informacion de clase mayoritaria → underfitting |
| **Oversampling** | Conserva todos los datos | Overfitting por replicacion exacta |
| **SMOTE** | Genera datos sinteticos nuevos (interpolacion k-NN) | Ruido en zonas de solapamiento, lento en datasets grandes |

### Regresion Logistica
- Estandar de oro en sectores regulados por su **interpretabilidad**
- Clave: calibracion dinamica del threshold (no usar 0.5 por defecto)
- Threshold 0.2 → alto Recall, muchos FP | Threshold 0.78 → alta Precision, muchos FN
- Basado en: Bayes Minimum Risk Classifier + matrices de costo real

### Random Forest
- Ensamble paralelo (Bagging): inmune al overfitting en datos ruidosos
- `class_weight='balanced'`: penaliza errores en clase minoritaria proporcionalmente
- `bootstrap=True`: diversidad en patrones aprendidos
- `max_features='sqrt'`: ninguna variable domina (evita sesgo por `amount`)
- F1-Score y AUC-ROC reportados >97% en literatura con buena hiperparametrizacion

### CatBoost
- GBDT secuencial y aditivo (cada arbol corrige errores del anterior)
- **Ventaja 1:** Manejo nativo de variables categoricas (Ordered Target Encoding) — evita Target Leakage
- **Ventaja 2:** Oblivious Trees (arboles simetricos) → latencia ultrabaja en produccion
- Supera XGBoost y LightGBM en datos desbalanceados: AUC 0.9837, F1 >86.36%
- Brier Score: 0.0004 (calibracion probabilistica casi perfecta)

---

## 5. Etica Algorítmica (FAccT)

### Principios FAccT
| Pilar | Descripcion | Riesgo en este proyecto |
|-------|-------------|------------------------|
| **Fairness** (Equidad) | Sin discriminacion sistematica | Sesgo contra perfiles "thin-file", zonas marginadas, genero |
| **Accountability** (Rendicion de cuentas) | Responsabilidad clara por decisiones del modelo | Modelo "caja negra" impide auditar quien es responsable |
| **Transparency** (Transparencia) | El ciudadano tiene derecho a saber por que fue bloqueado | RF y CatBoost son inherentemente opacos |

### Sesgo algoritmico
- IA entrenada con datos historicos sesgados perpetua desigualdades sociodemograficas
- Afecta desproporcionadamente: mujeres emprendedoras, poblaciones rurales, minorias etnicas, clientes "thin-file"
- Viola Art. 15 Constitucion y principio de igualdad material

### Problema de la Caja Negra
- RF y CatBoost logran AUC >0.99 pero son inescrutables
- El banco no puede responder "el algoritmo lo decidio" ante un juez de tutela

### Solucion: XAI (Explainable AI)
- **SHAP** (SHapley Additive exPlanations): asigna contribucion exacta de cada variable a la prediccion. Basado en teoria de juegos cooperativa (Premio Nobel Lloyd Shapley)
- **LIME** (Local Interpretable Model-Agnostic Explanations): aproxima el comportamiento local del modelo con un modelo lineal interpretable

---

## 6. Aplicacion a Banco Falabella

### Por que Banco Falabella es relevante
- Origen retail → base de clientes masiva y diversa → mayor riesgo de sesgo algoritmico
- Tarjeta CMR → alta exposicion a fraude CNP (Card-Not-Present) en e-commerce
- Vigilado por SFC → aplica todo el marco legal colombiano descrito
- Canales digitales activos → genera el tipo de datos transaccionales del dataset PaySim

### Fuentes para el informe
- Reportes anuales: Grupo Falabella (falabella.com)
- Supervision: Superintendencia Financiera de Colombia (superfinanciera.gov.co)
- Marco legal: Referencias 6-30 de `investigacion_marco_teorico.pdf`
- Modelos y tecnicas: Referencias 1-3, 31-32, 43-44, 55-67 del mismo documento
