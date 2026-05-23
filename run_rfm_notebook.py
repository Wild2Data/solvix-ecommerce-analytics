"""
Construye notebooks/04_rfm_segmentation.ipynb con outputs ejecutados.
Ejecutar desde la raiz del proyecto con: python -X utf8 run_rfm_notebook.py
"""
import sys, io, json, traceback, base64, os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# CONTENIDO DE LAS CELDAS
# Todas las cadenas usan concatenacion para evitar problemas de codificacion
# ---------------------------------------------------------------------------

MD = {}   # Markdown cells
CD = {}   # Code cells

MD[0] = (
    "# 04 - Segmentacion RFM de Clientes\n"
    "\n"
    "**Objetivo:** Clasificar la base de clientes usando el modelo RFM "
    "(Recency, Frequency, Monetary) para identificar segmentos accionables "
    "que informen la estrategia de retencion y reactivacion.\n"
    "\n"
    "**Periodo de analisis:** Noviembre 2025 - Abril 2026  \n"
    "**Base:** 3 500 ordenes - 1 404 clientes unicos  \n"
    "**Referencia temporal:** 30 de abril de 2026\n"
    "\n"
    "---\n"
    "\n"
    "El modelo RFM asigna a cada cliente tres puntuaciones (1-5) segun:\n"
    "\n"
    "| Dimension | Pregunta de negocio | Mejor score |\n"
    "|---|---|---|\n"
    "| **Recency (R)** | Dias desde la ultima compra | Pocos dias = 5 |\n"
    "| **Frequency (F)** | Numero de ordenes en el periodo | Muchas = 5 |\n"
    "| **Monetary (M)** | Ingreso total acumulado (USD) | Mayor gasto = 5 |\n"
    "\n"
    "Los tres scores se combinan para asignar un segmento de negocio "
    "con acciones especificas de marketing."
)

CD[1] = (
    "import pandas as pd\n"
    "import numpy as np\n"
    "import matplotlib\n"
    "matplotlib.use('Agg')\n"
    "import matplotlib.pyplot as plt\n"
    "import warnings\n"
    "warnings.filterwarnings('ignore')\n"
    "\n"
    "plt.rcParams.update({\n"
    "    'figure.dpi': 120,\n"
    "    'font.size': 10,\n"
    "    'axes.spines.top': False,\n"
    "    'axes.spines.right': False,\n"
    "    'axes.grid': True,\n"
    "    'grid.alpha': 0.3,\n"
    "})\n"
    "\n"
    "print('Librerias cargadas')\n"
    "print(f'  pandas     {pd.__version__}')\n"
    "print(f'  numpy      {np.__version__}')\n"
    "print(f'  matplotlib {matplotlib.__version__}')"
)

MD[2] = (
    "## 1. Carga y preparacion de datos\n"
    "\n"
    "Se leen las ordenes limpias del pipeline de EDA (notebook 02). "
    "La fecha de referencia es el ultimo dia del periodo: **2026-04-30**."
)

CD[3] = (
    "df = pd.read_csv('data/processed/solvix_ordenes_clean.csv', parse_dates=['Fecha'])\n"
    "\n"
    "FECHA_REF = pd.Timestamp('2026-04-30')\n"
    "\n"
    "print(f'Ordenes cargadas : {len(df):,}')\n"
    "print(f'Clientes unicos  : {df[\"ID_Cliente\"].nunique():,}')\n"
    "print(f'Rango de fechas  : {df[\"Fecha\"].min().date()} al {df[\"Fecha\"].max().date()}')\n"
    "print(f'Fecha referencia : {FECHA_REF.date()}')\n"
    "df.head(3)"
)

MD[4] = (
    "## 2. Calculo de metricas RFM brutas\n"
    "\n"
    "Para cada cliente se calculan:\n"
    "- **Recency:** dias transcurridos desde su ultima compra hasta la fecha de referencia\n"
    "- **Frequency:** numero de ordenes colocadas en el periodo\n"
    "- **Monetary:** ingreso total acumulado (USD)"
)

CD[5] = (
    "rfm_raw = (\n"
    "    df.groupby('ID_Cliente')\n"
    "    .agg(\n"
    "        ultima_compra  = ('Fecha', 'max'),\n"
    "        frecuencia     = ('ID_Orden', 'count'),\n"
    "        monetario      = ('Ingreso_Total', 'sum'),\n"
    "    )\n"
    "    .reset_index()\n"
    ")\n"
    "\n"
    "rfm_raw['recencia'] = (FECHA_REF - rfm_raw['ultima_compra']).dt.days\n"
    "\n"
    "print(f'Clientes en tabla RFM: {len(rfm_raw):,}')\n"
    "print()\n"
    "print(rfm_raw[['ID_Cliente','recencia','frecuencia','monetario']].describe().round(1))"
)

MD[6] = (
    "## 3. Scoring por quintiles (1-5)\n"
    "\n"
    "Cada metrica se divide en 5 cuantiles iguales. El score 5 siempre indica el perfil mas valioso:\n"
    "- **R**: score 5 = compro mas recientemente\n"
    "- **F**: score 5 = mayor numero de ordenes\n"
    "- **M**: score 5 = mayor gasto acumulado\n"
    "\n"
    "El `rfm_score` combinado es la suma R+F+M (rango 3-15)."
)

CD[7] = (
    "rfm = rfm_raw.copy()\n"
    "\n"
    "rfm['R'] = pd.qcut(rfm['recencia'], q=5, labels=[5,4,3,2,1]).astype(int)\n"
    "rfm['F'] = pd.qcut(rfm['frecuencia'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)\n"
    "rfm['M'] = pd.qcut(rfm['monetario'].rank(method='first'), q=5, labels=[1,2,3,4,5]).astype(int)\n"
    "\n"
    "rfm['rfm_score'] = rfm['R'] + rfm['F'] + rfm['M']\n"
    "rfm['rf_label']  = rfm['R'].astype(str) + rfm['F'].astype(str)\n"
    "\n"
    "print('Distribucion de scores por dimension:')\n"
    "for col in ['R','F','M']:\n"
    "    print(f'  {col}: {dict(rfm[col].value_counts().sort_index())}')\n"
    "print()\n"
    "print(f'RFM score - min: {rfm[\"rfm_score\"].min()}  max: {rfm[\"rfm_score\"].max()}  media: {rfm[\"rfm_score\"].mean():.1f}')\n"
    "rfm[['ID_Cliente','R','F','M','rfm_score','recencia','frecuencia','monetario']].head(8)"
)

MD[8] = (
    "## 4. Asignacion de segmentos\n"
    "\n"
    "Se aplica la matriz estandar de segmentos RFM basada en la combinacion R-F. "
    "Esta matriz es ampliamente usada en e-commerce para derivar acciones de marketing directas."
)

CD[9] = (
    "def asignar_segmento(r, f):\n"
    "    if r >= 4 and f >= 4:      return 'Champions'\n"
    "    elif r >= 3 and f >= 3:    return 'Leales'\n"
    "    elif r >= 4 and f <= 2:    return 'Clientes Recientes'\n"
    "    elif r == 3 and f <= 2:    return 'Prometedores'\n"
    "    elif r == 2 and f >= 4:    return 'En Riesgo'\n"
    "    elif r <= 2 and f >= 4:    return 'No Perder'\n"
    "    elif r == 2 and f <= 2:    return 'Por Despertar'\n"
    "    elif r <= 2 and f >= 2:    return 'Hibernando'\n"
    "    else:                      return 'Perdidos'\n"
    "\n"
    "rfm['segmento'] = rfm.apply(lambda x: asignar_segmento(x['R'], x['F']), axis=1)\n"
    "\n"
    "resumen = (\n"
    "    rfm.groupby('segmento')\n"
    "    .agg(\n"
    "        clientes        = ('ID_Cliente', 'count'),\n"
    "        recencia_avg    = ('recencia', 'mean'),\n"
    "        frecuencia_avg  = ('frecuencia', 'mean'),\n"
    "        monetario_avg   = ('monetario', 'mean'),\n"
    "        monetario_total = ('monetario', 'sum'),\n"
    "    )\n"
    "    .round(1)\n"
    "    .sort_values('monetario_total', ascending=False)\n"
    "    .reset_index()\n"
    ")\n"
    "\n"
    "resumen['pct_clientes'] = (resumen['clientes'] / resumen['clientes'].sum() * 100).round(1)\n"
    "resumen['pct_ingreso']  = (resumen['monetario_total'] / resumen['monetario_total'].sum() * 100).round(1)\n"
    "\n"
    "print(resumen.to_string(index=False))"
)

MD[10] = (
    "## 5. Visualizacion de segmentos\n"
    "\n"
    "### 5.1 Distribucion de clientes y valor por segmento"
)

CD[11] = (
    "PALETA = {\n"
    "    'Champions':          '#2ecc71',\n"
    "    'Leales':             '#27ae60',\n"
    "    'Clientes Recientes': '#3498db',\n"
    "    'Prometedores':       '#85c1e9',\n"
    "    'En Riesgo':          '#e74c3c',\n"
    "    'No Perder':          '#c0392b',\n"
    "    'Por Despertar':      '#bdc3c7',\n"
    "    'Hibernando':         '#95a5a6',\n"
    "    'Perdidos':           '#7f8c8d',\n"
    "}\n"
    "\n"
    "orden   = resumen['segmento'].tolist()\n"
    "colores = [PALETA.get(s, '#aaa') for s in orden]\n"
    "\n"
    "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n"
    "fig.suptitle('Distribucion de la Base de Clientes - Segmentacion RFM',\n"
    "             fontsize=13, fontweight='bold', y=1.01)\n"
    "\n"
    "ax1 = axes[0]\n"
    "bars = ax1.barh(orden, resumen['clientes'], color=colores, edgecolor='white', linewidth=0.5)\n"
    "ax1.set_xlabel('Numero de clientes')\n"
    "ax1.set_title('Clientes por segmento')\n"
    "ax1.invert_yaxis()\n"
    "for bar, val, pct in zip(bars, resumen['clientes'], resumen['pct_clientes']):\n"
    "    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,\n"
    "             f'{val}  ({pct}%)', va='center', fontsize=9)\n"
    "ax1.set_xlim(0, resumen['clientes'].max() * 1.35)\n"
    "\n"
    "ax2 = axes[1]\n"
    "bars2 = ax2.barh(orden, resumen['monetario_total'], color=colores, edgecolor='white', linewidth=0.5)\n"
    "ax2.set_xlabel('Ingreso total (USD)')\n"
    "ax2.set_title('Ingreso acumulado por segmento')\n"
    "ax2.invert_yaxis()\n"
    "for bar, val, pct in zip(bars2, resumen['monetario_total'], resumen['pct_ingreso']):\n"
    "    ax2.text(bar.get_width() + 100, bar.get_y() + bar.get_height()/2,\n"
    "             f'${val:,.0f}  ({pct}%)', va='center', fontsize=9)\n"
    "ax2.set_xlim(0, resumen['monetario_total'].max() * 1.45)\n"
    "\n"
    "plt.tight_layout()\n"
    "plt.savefig('data/processed/rfm_distribucion.png', bbox_inches='tight', dpi=130)\n"
    "print('Grafico 1 guardado.')"
)

MD[12] = (
    "### 5.2 Mapa de posicionamiento RFM (Recencia x Frecuencia)\n"
    "\n"
    "Cada punto representa un cliente. La posicion en el plano refleja su "
    "comportamiento reciente y habitual de compra. El eje X esta invertido: "
    "los clientes mas activos (recientes) aparecen a la izquierda."
)

CD[13] = (
    "fig, ax = plt.subplots(figsize=(10, 7))\n"
    "\n"
    "for seg, grupo in rfm.groupby('segmento'):\n"
    "    ax.scatter(\n"
    "        grupo['recencia'], grupo['frecuencia'],\n"
    "        c=PALETA.get(seg, '#aaa'), label=seg,\n"
    "        alpha=0.75, s=60, edgecolors='white', linewidths=0.4\n"
    "    )\n"
    "\n"
    "ax.set_xlabel('Recencia (dias desde ultima compra) - izquierda = mas reciente')\n"
    "ax.set_ylabel('Frecuencia (numero de ordenes)')\n"
    "ax.set_title('Mapa RFM - Posicionamiento de Clientes', fontsize=13, fontweight='bold')\n"
    "ax.invert_xaxis()\n"
    "ax.legend(title='Segmento', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8)\n"
    "\n"
    "plt.tight_layout()\n"
    "plt.savefig('data/processed/rfm_mapa.png', bbox_inches='tight', dpi=130)\n"
    "print('Grafico 2 guardado.')"
)

MD[14] = "### 5.3 Perfil de valor promedio por segmento"

CD[15] = (
    "fig, axes = plt.subplots(1, 2, figsize=(12, 5))\n"
    "fig.suptitle('Perfil de Valor por Segmento', fontsize=13, fontweight='bold')\n"
    "\n"
    "orden_m  = resumen.sort_values('monetario_avg', ascending=True)['segmento'].tolist()\n"
    "colores_m = [PALETA.get(s, '#aaa') for s in orden_m]\n"
    "vals_m    = resumen.set_index('segmento').loc[orden_m, 'monetario_avg']\n"
    "\n"
    "axes[0].barh(orden_m, vals_m, color=colores_m, edgecolor='white')\n"
    "axes[0].set_xlabel('Ingreso promedio por cliente (USD)')\n"
    "axes[0].set_title('Monetario promedio')\n"
    "for i, v in enumerate(vals_m):\n"
    "    axes[0].text(v + 5, i, f'${v:,.0f}', va='center', fontsize=9)\n"
    "axes[0].set_xlim(0, vals_m.max() * 1.25)\n"
    "\n"
    "orden_f   = resumen.sort_values('frecuencia_avg', ascending=True)['segmento'].tolist()\n"
    "colores_f = [PALETA.get(s, '#aaa') for s in orden_f]\n"
    "vals_f    = resumen.set_index('segmento').loc[orden_f, 'frecuencia_avg']\n"
    "\n"
    "axes[1].barh(orden_f, vals_f, color=colores_f, edgecolor='white')\n"
    "axes[1].set_xlabel('Ordenes promedio por cliente')\n"
    "axes[1].set_title('Frecuencia promedio')\n"
    "for i, v in enumerate(vals_f):\n"
    "    axes[1].text(v + 0.1, i, f'{v:.1f}', va='center', fontsize=9)\n"
    "axes[1].set_xlim(0, vals_f.max() * 1.2)\n"
    "\n"
    "plt.tight_layout()\n"
    "plt.savefig('data/processed/rfm_valor.png', bbox_inches='tight', dpi=130)\n"
    "print('Grafico 3 guardado.')"
)

MD[16] = (
    "## 6. Hallazgos clave y recomendaciones\n"
    "\n"
    "El analisis RFM revela la estructura real del negocio mas alla del revenue agregado.\n"
    "Los segmentos de accion prioritaria son:"
)

CD[17] = (
    "acciones = [\n"
    "    ('Champions',          'Referral program + early access to new products.'),\n"
    "    ('Leales',             'Loyalty discount on next order. Goal: move to Champions.'),\n"
    "    ('En Riesgo',          'Urgent reactivation: personalized email with limited offer.'),\n"
    "    ('No Perder',          'Direct outreach - high-value clients going inactive. VIP offer.'),\n"
    "    ('Clientes Recientes', 'Onboarding: incentivize second purchase within 15 days.'),\n"
    "    ('Prometedores',       'Increase frequency via cross-sell of related categories.'),\n"
    "    ('Hibernando',         'Low-cost email/push campaign. Recoverable with right offer.'),\n"
    "    ('Perdidos',           'No paid investment. Organic retargeting only.'),\n"
    "]\n"
    "\n"
    "print('RECOMENDACIONES POR SEGMENTO')\n"
    "print('=' * 65)\n"
    "for seg, accion in acciones:\n"
    "    n = resumen[resumen['segmento'] == seg]['clientes'].values\n"
    "    n_str = '(' + str(n[0]) + ' clientes)' if len(n) > 0 else ''\n"
    "    print('  >> ' + seg + ' ' + n_str)\n"
    "    print('     ' + accion)\n"
    "\n"
    "top2 = resumen[resumen['segmento'].isin(['Champions','Leales'])]\n"
    "n_top2   = top2['clientes'].sum()\n"
    "pct_top2 = round(n_top2 / resumen['clientes'].sum() * 100, 1)\n"
    "ing_top2 = top2['monetario_total'].sum()\n"
    "pct_ing  = round(ing_top2 / resumen['monetario_total'].sum() * 100, 1)\n"
    "\n"
    "print()\n"
    "print('=' * 65)\n"
    "print('Champions + Leales: ' + str(n_top2) + ' clientes (' + str(pct_top2) + '%) '\n"
    "      'generan $' + '{:,.0f}'.format(ing_top2) + ' (' + str(pct_ing) + '% del ingreso total)')"
)

MD[18] = (
    "## 7. Exportar resultados para Power BI\n"
    "\n"
    "Se exportan dos archivos:\n"
    "- `rfm_clientes.csv` - tabla cliente-nivel con scores y segmento (pagina Clientes del dashboard)\n"
    "- `rfm_resumen_segmentos.csv` - metricas agregadas por segmento"
)

CD[19] = (
    "export = rfm[[\n"
    "    'ID_Cliente','R','F','M','rfm_score','segmento',\n"
    "    'recencia','frecuencia','monetario','ultima_compra'\n"
    "]].sort_values('rfm_score', ascending=False)\n"
    "\n"
    "export.to_csv('data/processed/rfm_clientes.csv', index=False)\n"
    "print(f'rfm_clientes.csv exportado - {len(export):,} filas')\n"
    "\n"
    "resumen.to_csv('data/processed/rfm_resumen_segmentos.csv', index=False)\n"
    "print(f'rfm_resumen_segmentos.csv exportado - {len(resumen)} segmentos')\n"
    "\n"
    "print()\n"
    "print('Vista previa rfm_clientes.csv:')\n"
    "export.head(5)"
)

# ---------------------------------------------------------------------------
# RUNNER
# ---------------------------------------------------------------------------

def run_cell(code_str, globs):
    buf = io.StringIO()
    images = []
    sys.stdout, old = buf, sys.stdout
    err = None
    try:
        exec(compile(code_str, '<cell>', 'exec'), globs)
        if 'plt' in globs and globs['plt'].get_fignums():
            b = io.BytesIO()
            globs['plt'].savefig(b, format='png', bbox_inches='tight', dpi=120)
            b.seek(0)
            images.append(base64.b64encode(b.read()).decode())
            globs['plt'].close('all')
    except Exception:
        err = traceback.format_exc()
    finally:
        sys.stdout = old
    return buf.getvalue(), err, images

def md_cell(src):
    return {"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)}

def code_cell(src, n, stdout, err, imgs):
    outs = []
    if stdout.strip():
        outs.append({"output_type": "stream", "name": "stdout",
                     "text": stdout.splitlines(keepends=True)})
    for img in imgs:
        outs.append({"output_type": "display_data", "metadata": {},
                     "data": {"image/png": img, "text/plain": ["<Figure>"]}})
    if err:
        outs.append({"output_type": "stream", "name": "stderr",
                     "text": err.splitlines(keepends=True)})
    return {"cell_type": "code", "execution_count": n, "metadata": {},
            "source": src.splitlines(keepends=True), "outputs": outs}

# Orden de celdas: MD[0], CD[1], MD[2], CD[3], ... MD[18], CD[19]
ORDER = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]

globs = {"__name__": "__main__"}
cells = []
n = 1

for idx in ORDER:
    is_code = idx in CD
    if not is_code:
        cells.append(md_cell(MD[idx]))
        continue
    src = CD[idx]
    print(f"Cell [{n}] running...")
    out, err, imgs = run_cell(src, globs)
    if out: print(out.rstrip())
    if err: print("ERROR:\n" + err)
    cells.append(code_cell(src, n, out, err, imgs))
    n += 1

notebook = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3 (Anaconda)",
                       "language": "python", "name": "anaconda3"},
        "language_info": {"name": "python", "version": "3.11.0"}
    },
    "cells": cells
}

out_path = os.path.join('notebooks', '04_rfm_segmentation.ipynb')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)

print(f"\nNotebook guardado: {out_path} ({len(cells)} celdas)")
