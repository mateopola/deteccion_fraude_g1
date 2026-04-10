"""
Convierte citas APA inline → formato IEEE [n] en generar_informe.py.
Ejecutar una vez: python apply_ieee.py
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('generar_informe.py', 'r', encoding='utf-8') as f:
    t = f.read()

# ─── SUSTITUCIONES ────────────────────────────────────────────────────────────
# Orden: patrones más específicos / largos primero para evitar reemplazos parciales

subs = [
    # ── Multi-cita compuestas ────────────────────────────────────────────────
    ('(Código Penal — Ley 599/2000; Código Civil; Constitución Política de Colombia, 1991)',
     '[8][9][10]'),
    ('(Art. 246/2341, Art. 15 CN, Sentencia T-255/22)',
     '[8][9][10][11]'),
    ('Chawla et al., 2002; He & Garcia, 2009; Prokhorenkova et al., 2018; '
     'Obermeyer et al., 2019; Dal Pozzolo et al., 2015; Breiman, 2001',
     '[4][15][6][21][18][5]'),
    ('(Chawla et al., 2002; He & Garcia, 2009; Fernández et al., 2018)',
     '[4][15][33]'),
    ('(Chawla et al., 2002; He & Garcia, 2009)',
     '[4][15]'),
    ('(Euromonitor International — Passport, 2024; Nilson Report, 2023)',
     '[19][1]'),
    ('(Bahnsen et al., 2016; Dal Pozzolo et al., 2015)',
     '[30][18]'),
    ('(Obermeyer et al., Science 2019; Eubanks, 2018)',
     '[21][25]'),
    ('(Obermeyer et al., 2019; Eubanks, 2018)',
     '[21][25]'),
    ('(Lundberg & Lee, 2017; Ribeiro et al., 2016)',
     '[13][14]'),
    ('(Cherif et al., 2023 — arXiv:2303.06514; IJSDR2401084)',
     '[38][39]'),
    ('(IJSDR2401084; ResearchGate 349156860)',
     '[39][40]'),
    ('(Elkan, 2001; Bahnsen et al., 2016)',
     '[7][30]'),

    # ── Sentencias / legales mixtos ──────────────────────────────────────────
    ('(Art. 15 CN, Sentencia T-255/22 — Corte Constitucional, 2022)',
     '[10][11]'),
    ('(Sentencia T-255/22 — Corte Constitucional, 2022)',
     '[11]'),
    ('(Sentencia SC3146-2020 — Corte Suprema, 2020)',
     '[44]'),
    ('(Corte Constitucional, Sentencia T-255/22)',
     '[11]'),
    ('Sentencia T-255/22 — Corte Constitucional, 2022',   # sin paréntesis externo
     'Sentencia T-255/22 [11]'),

    # ── Paréntesis mixtos texto+cita ─────────────────────────────────────────
    ('(crecimiento >250% en 5 años en América Latina — Euromonitor International, 2024)',
     '(crecimiento >250% en 5 años en América Latina [16])'),
    ('(Bayes Minimum Risk Classifier — Duda et al., 2001)',
     '(Bayes Minimum Risk Classifier [35])'),
    ('(Cost-Sensitive Learning — Elkan, 2001; Bahnsen et al., 2016)',
     '(Cost-Sensitive Learning [7][30])'),
    ('(Premio Nobel — Shapley, 1953)',
     '(Premio Nobel [46])'),

    # ── Citas Euromonitor con texto circundante ───────────────────────────────
    ('Según Euromonitor International — Passport (2024),',
     'Según [19],'),
    # El "(2024)" genérico de Euromonitor Passport en medio de texto:
    ('Euromonitor International — Passport (2024)',
     'Euromonitor International [19]'),
    # Citas sueltas Euromonitor
    ('(Euromonitor International, 2024)',
     '[16]'),
    ('Euromonitor International, 2024',     # sin paréntesis (ya capturado arriba si tiene)
     'Euromonitor International [16]'),

    # ── Citas legales sueltas ────────────────────────────────────────────────
    ('(Decreto 1674/2021)',   '[2]'),
    ('(Ley 1266/2008, Art. 2341 C.C.)', '[22][9]'),
    ('(Ley 1266/2008)',       '[22]'),
    ('Ley 1266/2008',         'Ley 1266/2008 [22]'),   # aparece sin paréntesis en algunas partes
    ('(Ley 1328/2009, Art. 3)', '[23]'),
    ('Circular SFC 029/2014', 'Circular SFC 029/2014 [24]'),   # sin paréntesis en el texto
    ('(Circular SFC 029/2014)', '[24]'),
    ('(Sentencia T-255/22)',   '[11]'),
    ('Sentencia T-255/22',     'Sentencia T-255/22 [11]'),  # residuo sin paréntesis
    ('(Art. 2341 C.C.)',       '[9]'),
    ('Art. 2341 C.C.',         'Art. 2341 C.C. [9]'),

    # ── Autores académicos ───────────────────────────────────────────────────
    ('(Nilson Report, 2023)',             '[1]'),
    ('Nilson Report, 2023',              'Nilson Report [1]'),
    ('(Chapman et al., 2000)',           '[3]'),
    ('(Chawla et al., 2002)',            '[4]'),
    ('(Breiman, 2001)',                  '[5]'),
    ('(Prokhorenkova et al., 2018)',     '[6]'),
    ('(Elkan, 2001)',                    '[7]'),
    ('(FAccT — ACM, 2020)',              '[12]'),
    ('(ACM, 2020)',                      '[12]'),
    ('(Lundberg & Lee, 2017)',           '[13]'),
    ('(Lundberg & Lee, NeurIPS 2017)',   '[13]'),
    ('(Ribeiro et al., 2016)',           '[14]'),
    ('(Ribeiro et al., KDD 2016)',       '[14]'),
    ('(He & Garcia, 2009)',              '[15]'),
    ('He & Garcia (2009)',               '[15]'),
    ('(Kaggle, 2017)',                   '[17]'),
    ('(Dal Pozzolo et al., 2015)',       '[18]'),
    ('Dal Pozzolo et al., 2015',         'Dal Pozzolo et al. [18]'),  # residual
    ('(Grupo Falabella, Memoria Anual 2023)', '[20]'),
    ('(Obermeyer et al., 2019)',         '[21]'),
    ('Obermeyer et al., 2019',           'Obermeyer et al. [21]'),
    ('(Kaufman et al., 2012)',           '[26]'),
    ('(Han et al., 2011)',               '[27]'),
    ('(Branco et al., 2016)',            '[28]'),
    ('(Branco et al., 2016 — MDPI ISSN 2078-2489)', '[28]'),
    ('(Tukey, 1977)',                    '[29]'),
    ('(Bahnsen et al., 2016)',           '[30]'),
    ('Bahnsen et al. (2016)',            '[30]'),
    ('(López et al., 2022)',             '[31]'),
    ('(Hipel & McLeod, 1994)',           '[32]'),
    ('(Fernández et al., 2018)',         '[33]'),
    ('Fernández et al. (2018)',          '[33]'),
    ('(Hosmer & Lemeshow, 2000)',        '[34]'),
    ('(Díez-Pastor et al., 2015)',       '[36]'),
    ('(Oshiro et al., 2012)',            '[37]'),
    ('(Zhang et al., 2022 — ResearchGate 349156860)', '[40]'),
    ('(Islam & Chowdhury, 2022 — ref. 1 marco teórico)', '[41]'),
    ('(Davis & Goadrich, 2006)',         '[42]'),
    ('(Lopez-Rojas et al., 2016)',       '[43]'),
    ('(Lipton, 2018)',                   '[45]'),
    ('Chawla et al. (2002)',             '[4]'),
]

for old, new in subs:
    t = t.replace(old, new)

# ─── LISTA DE REFERENCIAS (reemplazar la lista refs completa) ─────────────────
OLD_REFS_START = "refs = ["
OLD_REFS_END   = "]"

NEW_REFS = '''refs = [
    '[1] Nilson Report. (2023). Global card fraud losses 2022: USD 33.5 billion. Issue 1229.',

    '[2] Decreto 1674 de 2021. SARLAFT 4.0. Ministerio de Hacienda y Crédito Público. Colombia.',

    '[3] P. Chapman, J. Clinton, R. Kerber, T. Khabaza, T. Reinartz, C. Shearer, and R. Wirth, '
    '"CRISP-DM 1.0: Step-by-step data mining guide," SPSS Inc., 2000.',

    '[4] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer, "SMOTE: Synthetic Minority '
    'Over-sampling Technique," J. Artif. Intell. Res., vol. 16, pp. 321–357, 2002.',

    '[5] L. Breiman, "Random forests," Mach. Learn., vol. 45, no. 1, pp. 5–32, 2001. '
    'https://doi.org/10.1023/A:1010933404324',

    '[6] L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorogush, and A. Gulin, "CatBoost: '
    'unbiased boosting with categorical features," NeurIPS, vol. 31, 2018.',

    '[7] C. Elkan, "The foundations of cost-sensitive learning," in Proc. IJCAI-01, pp. 973–978, 2001.',

    '[8] Código Penal Colombiano. Arts. 246, 316, 323, 327. Ley 599 de 2000.',

    '[9] Código Civil Colombiano. Art. 2341 — Responsabilidad civil extracontractual. Ley 57 de 1887.',

    '[10] Constitución Política de Colombia. (1991). Arts. 13 y 15. Bogotá: Imprenta Nacional.',

    '[11] Corte Constitucional de Colombia. (2022). Sentencia T-255/22. M.P.: Diana Fajardo Rivera.',

    '[12] ACM FAccT. (2020). Fairness, Accountability, and Transparency in Machine Learning. '
    'Proc. 2020 ACM Conference on FAccT. ACM Press.',

    '[13] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," '
    'NeurIPS, vol. 30, 2017.',

    '[14] M. T. Ribeiro, S. Singh, and C. Guestrin, "\\"Why should I trust you?\\": Explaining '
    'the predictions of any classifier," in Proc. KDD 2016, pp. 1135–1144. ACM.',

    '[15] H. He and E. A. Garcia, "Learning from imbalanced data," IEEE Trans. Knowl. Data Eng., '
    'vol. 21, no. 9, pp. 1263–1284, 2009.',

    '[16] Euromonitor International. (2024). Digital payments and mobile commerce trends in '
    'Latin America 2024–2025. https://www.portal.euromonitor.com/magazine/homemain',

    '[17] PaySim. (2017). Synthetic Financial Datasets For Fraud Detection. Kaggle. '
    'https://www.kaggle.com/datasets/ealaxi/paysim1',

    '[18] A. Dal Pozzolo, O. Caelen, Y.-A. Le Borgne, S. Waterschoot, and G. Bontempi, '
    '"Learned lessons in credit card fraud detection from a practitioner perspective," '
    'Expert Syst. Appl., vol. 41, no. 10, pp. 4915–4928, 2015.',

    '[19] Euromonitor International — Passport. (2024). Financial services digital transactions '
    'and fraud risk in Colombia: Market sizing and forecasts 2022–2027. '
    'Passport Database. https://www.portal.euromonitor.com/magazine/homemain',

    '[20] Grupo Falabella. (2023). Memoria Anual 2023. Santiago de Chile: Grupo Falabella S.A. '
    'https://www.falabella.com/inversionistas',

    '[21] Z. Obermeyer, B. Powers, C. Vogeli, and S. Mullainathan, "Dissecting racial bias '
    'in an algorithm used to manage the health of populations," Science, vol. 366, no. 6464, '
    'pp. 447–453, 2019.',

    '[22] Ley 1266 de 2008. Hábeas Data Financiero. Colombia.',

    '[23] Ley 1328 de 2009. Protección al consumidor financiero, Art. 3. Colombia.',

    '[24] Circular Externa SFC 029/2014 y actualizaciones 2024. Superintendencia Financiera de Colombia.',

    '[25] V. Eubanks, Automating Inequality: How High-Tech Tools Profile, Police, and Punish the Poor. '
    'St. Martin\'s Press, 2018.',

    '[26] S. Kaufman, S. Rosset, C. Perlich, and O. Stitelman, "Leakage in data mining: '
    'Formulation, detection, and avoidance," ACM TKDD, vol. 6, no. 4, pp. 1–21, 2012.',

    '[27] J. Han, M. Kamber, and J. Pei, Data Mining: Concepts and Techniques, 3rd ed. '
    'Morgan Kaufmann, 2011.',

    '[28] P. Branco, L. Torgo, and R. P. Ribeiro, "A survey of predictive modeling on imbalanced '
    'domains," ACM Comput. Surv., vol. 49, no. 2, pp. 1–50, 2016. MDPI ISSN 2078-2489.',

    '[29] J. W. Tukey, Exploratory Data Analysis. Addison-Wesley, 1977.',

    '[30] A. C. Bahnsen, D. Aouada, A. Stojanovic, and B. Ottersten, "Feature engineering '
    'strategies for credit card fraud detection," Expert Syst. Appl., vol. 51, pp. 134–142, 2016. '
    'https://doi.org/10.1016/j.eswa.2015.12.030',

    '[31] E. López et al. (2022). Fraud detection patterns in synthetic financial datasets. '
    'Referencia del marco teórico del proyecto.',

    '[32] K. W. Hipel and A. I. McLeod, Time Series Modelling of Water Resources and '
    'Environmental Systems. Elsevier, 1994.',

    '[33] A. Fernández, S. García, M. Galar, R. C. Prati, B. Krawczyk, and F. Herrera, '
    'Learning from Imbalanced Data Sets. Springer, 2018. '
    'https://doi.org/10.1007/978-3-319-98074-4',

    '[34] D. W. Hosmer and S. Lemeshow, Applied Logistic Regression, 2nd ed. Wiley, 2000.',

    '[35] R. O. Duda, P. E. Hart, and D. G. Stork, Pattern Classification, 2nd ed. '
    'New York: Wiley-Interscience, 2001.',

    '[36] J. F. Díez-Pastor, J. J. Rodríguez, C. García-Osorio, and L. I. Kuncheva, '
    '"Diversity techniques improve the performance of the best imbalance learning ensembles," '
    'Inf. Sci., vol. 325, pp. 98–117, 2015.',

    '[37] T. M. Oshiro, P. S. Perez, and J. A. Baranauskas, "How many trees in a random forest?" '
    'in Proc. MLDM 2012, pp. 154–168. Springer.',

    '[38] A. Cherif et al., "Credit card fraud detection in the era of disruptive technologies: '
    'A systematic review," arXiv:2303.06514, 2023.',

    '[39] IJSDR2401084. (2024). Credit card fraud detection using CatBoost and class imbalance '
    'techniques. International Journal of Scientific Development and Research, vol. 9, no. 1.',

    '[40] W. Zhang, Z. Xu, W. He, and Y. Li, "Credit fraud detection using CatBoost gradient '
    'boosting with optimized hyperparameters," ResearchGate ID: 349156860, 2022.',

    '[41] M. R. Islam and M. Chowdhury, "CatBoost for financial fraud detection," '
    'ResearchGate ID: 349156860, 2022.',

    '[42] J. Davis and M. Goadrich, "The relationship between precision-recall and ROC curves," '
    'in Proc. 23rd ICML, pp. 233–240. ACM, 2006.',

    '[43] E. A. Lopez-Rojas, A. Elmir, and S. Axelsson, "PaySim: A financial mobile money '
    'simulator for fraud detection," in Proc. 28th EMSS 2016, pp. 249–255. DIME Univ. of Genoa.',

    '[44] Corte Suprema de Justicia de Colombia. (2020). Sentencia SC3146-2020. Sala de Casación Civil.',

    '[45] Z. C. Lipton, "The mythos of model interpretability," Queue, vol. 16, no. 3, pp. 31–57, 2018.',

    '[46] L. S. Shapley, "A value for n-person games," Contributions to the Theory of Games, '
    'vol. 2, pp. 307–317. Princeton University Press, 1953.',

    '[47] Superintendencia Financiera de Colombia (SFC). Registro de entidades vigiladas. '
    'https://www.superfinanciera.gov.co/entidades-vigiladas',
]'''

# Locate and replace the refs list
start_idx = t.find('\nrefs = [')
if start_idx == -1:
    start_idx = t.find('refs = [')
end_marker = '\nfor ref in refs:'
end_idx = t.find(end_marker)
if start_idx != -1 and end_idx != -1:
    t = t[:start_idx+1] + NEW_REFS + '\n' + t[end_idx:]
    print("✓ Lista de referencias reemplazada")
else:
    print("✗ No se encontró la lista de referencias — revisar manualmente")

# Actualizar el print final para mostrar "IEEE" en lugar de "APA"
t = t.replace('print(f"Referencias APA: {len(refs)}")',
               'print(f"Referencias IEEE: {len(refs)}")')

with open('generar_informe.py', 'w', encoding='utf-8') as f:
    f.write(t)

print("✓ generar_informe.py actualizado con citas IEEE")
print("  Ejecuta: python generar_informe.py")
