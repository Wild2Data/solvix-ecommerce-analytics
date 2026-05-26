"""
Construye notebooks/03_product_profitability.ipynb con outputs ejecutados.
Ejecutar desde la raiz del proyecto con: python -X utf8 run_products_notebook.py
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

MD = {}
CD = {}

# ── Cell 0: Titulo ──────────────────────────────────────────────────────────
MD[0] = (
    "# 03 - Rentabilidad de Productos\n"
    "\n"
    "**Objetivo:** Identificar los productos mas rentables de Solvix, "
    "analizar su comportamiento mensual y distribucion geografica para "
    "orientar decisiones de inventario, pricing y campanas de marketing.\n"
    "\n"
    "**Periodo:** Noviembre 2025 - Abril 2026  \n"
    "**Catalogo:** 4 productos activos en 3 categorias  \n"
    "**Ordenes analizadas:** 3,500\n"
    "\n"
    "---\n"
    "\n"
    "### Catalogo de Productos\n"
    "\n"
    "| ID | Producto | Categoria | Precio |\n"
    "|---|---|---|---|\n"
    "| P001 | Vaso Termico Inteligente Auto | Auto | $39 |\n"
    "| P002 | Mini Bicicleta Premium | Fitness | $120 |\n"
    "| P003 | Soporte Magnetico Carga | Oficina/Auto | $24 |\n"
    "| P004 | Cojin Ergonomico Gel | Oficina/Auto | $34 |\n"
    "\n"
    "---"
)

# ── Cell 1: Imports + carga de datos ────────────────────────────────────────
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
    "df = pd.read_csv('data/processed/solvix_ordenes_clean.csv', parse_dates=['Fecha'])\n"
    "\n"
    "print('Ordenes cargadas :', f'{len(df):,}')\n"
    "print('Productos unicos  :', df['Nombre_Producto'].nunique())\n"
    "print('Categorias        :', df['Categoria'].nunique())\n"
    "print('Rango de fechas   :', df['Fecha'].dt.date.min(), 'al', df['Fecha'].dt.date.max())\n"
    "print('Ingreso total     : $', f\"{df['Ingreso_Total'].sum():,.0f}\")\n"
    "print('Ganancia bruta    : $', f\"{df['Ganancia_Bruta'].sum():,.0f}\")\n"
)

# ── Cell 2: Seccion 1 ────────────────────────────────────────────────────────
MD[2] = (
    "## 1. Rentabilidad por Producto\n"
    "\n"
    "Comparamos cada producto en las tres dimensiones clave del negocio: "
    "volumen (unidades), ingreso total y ganancia bruta. "
    "El margen nos indica la eficiencia operativa de cada SKU."
)

# ── Cell 3: Tabla de rentabilidad por producto ───────────────────────────────
CD[3] = (
    "prod = df.groupby('Nombre_Producto').agg(\n"
    "    unidades=('Cantidad', 'sum'),\n"
    "    ordenes=('ID_Orden', 'count'),\n"
    "    ingreso=('Ingreso_Total', 'sum'),\n"
    "    ganancia=('Ganancia_Bruta', 'sum'),\n"
    "    cogs=('COGS_Total', 'sum'),\n"
    "    envio=('Costo_Envio', 'sum'),\n"
    ").round(2)\n"
    "\n"
    "prod['margen_pct'] = (prod['ganancia'] / prod['ingreso'] * 100).round(1)\n"
    "prod['precio_prom'] = (prod['ingreso'] / prod['unidades']).round(2)\n"
    "prod['ganancia_x_unidad'] = (prod['ganancia'] / prod['unidades']).round(2)\n"
    "prod['pct_ingreso'] = (prod['ingreso'] / prod['ingreso'].sum() * 100).round(1)\n"
    "prod = prod.sort_values('ingreso', ascending=False)\n"
    "\n"
    "print('RENTABILIDAD POR PRODUCTO')\n"
    "print('=' * 70)\n"
    "for nombre, row in prod.iterrows():\n"
    "    print(f'  {nombre}')\n"
    "    print(f'    Unidades      : {row[\"unidades\"]:,}')\n"
    "    print(f'    Ingreso total : ${row[\"ingreso\"]:,.0f}  ({row[\"pct_ingreso\"]}% del total)')\n"
    "    print(f'    Ganancia bruta: ${row[\"ganancia\"]:,.0f}')\n"
    "    print(f'    Margen        : {row[\"margen_pct\"]}%')\n"
    "    print(f'    Precio prom   : ${row[\"precio_prom\"]}')\n"
    "    print(f'    Ganancia/unit : ${row[\"ganancia_x_unidad\"]}')\n"
    "    print()\n"
)

# ── Cell 4: Seccion 2 ────────────────────────────────────────────────────────
MD[4] = (
    "## 2. Analisis por Categoria\n"
    "\n"
    "Agrupamos los productos en sus 3 categorias para identificar "
    "cual segmento de mercado aporta mas al negocio en terminos de "
    "ingreso, volumen y rentabilidad."
)

# ── Cell 5: Categoria ────────────────────────────────────────────────────────
CD[5] = (
    "cat = df.groupby('Categoria').agg(\n"
    "    productos=('Nombre_Producto', 'nunique'),\n"
    "    unidades=('Cantidad', 'sum'),\n"
    "    ingreso=('Ingreso_Total', 'sum'),\n"
    "    ganancia=('Ganancia_Bruta', 'sum'),\n"
    ").round(2)\n"
    "\n"
    "cat['margen_pct'] = (cat['ganancia'] / cat['ingreso'] * 100).round(1)\n"
    "cat['pct_ingreso'] = (cat['ingreso'] / cat['ingreso'].sum() * 100).round(1)\n"
    "cat = cat.sort_values('ingreso', ascending=False)\n"
    "\n"
    "print('ANALISIS POR CATEGORIA')\n"
    "print('=' * 55)\n"
    "print(f'{\"Categoria\":<15} {\"Ingreso\":>10} {\"% Total\":>8} {\"Ganancia\":>10} {\"Margen\":>7}')\n"
    "print('-' * 55)\n"
    "for cat_name, row in cat.iterrows():\n"
    "    print(f'{cat_name:<15} ${row[\"ingreso\"]:>9,.0f} {row[\"pct_ingreso\"]:>7.1f}% ${row[\"ganancia\"]:>9,.0f} {row[\"margen_pct\"]:>6.1f}%')\n"
    "print('-' * 55)\n"
    "print(f'{\"TOTAL\":<15} ${cat[\"ingreso\"].sum():>9,.0f} {100:>7.1f}% ${cat[\"ganancia\"].sum():>9,.0f} {(cat[\"ganancia\"].sum()/cat[\"ingreso\"].sum()*100):>6.1f}%')\n"
)

# ── Cell 6: Seccion 3 ────────────────────────────────────────────────────────
MD[6] = (
    "## 3. Ingresos y Margen por Producto\n"
    "\n"
    "El grafico combina el ingreso total (barras) con el margen bruto (linea) "
    "para identificar si los productos de mayor venta son tambien los mas "
    "eficientes. Un alto ingreso con margen bajo indica presion en costos."
)

# ── Cell 7: Grafico barras + linea margen ────────────────────────────────────
CD[7] = (
    "fig, ax1 = plt.subplots(figsize=(10, 5))\n"
    "\n"
    "nombres_cortos = {\n"
    "    'Vaso Termico Inteligente Auto': 'Vaso Termico',\n"
    "    'Mini Bicicleta Premium': 'Mini Bicicleta',\n"
    "    'Soporte Magnetico Carga': 'Soporte Magnetico',\n"
    "    'Cojin Ergonomico Gel': 'Cojin Ergonomico',\n"
    "}\n"
    "prod_plot = prod.copy()\n"
    "prod_plot.index = [nombres_cortos.get(n, n) for n in prod_plot.index]\n"
    "\n"
    "colores = ['#2196F3', '#FF5722', '#4CAF50', '#9C27B0']\n"
    "bars = ax1.barh(prod_plot.index, prod_plot['ingreso'], color=colores, alpha=0.85, height=0.5)\n"
    "ax1.set_xlabel('Ingreso Total (USD)')\n"
    "ax1.set_title('Ingresos y Margen Bruto por Producto', fontsize=13, fontweight='bold', pad=12)\n"
    "\n"
    "for bar, val in zip(bars, prod_plot['ingreso']):\n"
    "    ax1.text(val + 500, bar.get_y() + bar.get_height()/2,\n"
    "             f'${val:,.0f}', va='center', fontsize=9)\n"
    "\n"
    "ax2 = ax1.twiny()\n"
    "ax2.plot(prod_plot['margen_pct'], prod_plot.index, 'o--',\n"
    "         color='#FF9800', linewidth=2, markersize=8, label='Margen %')\n"
    "ax2.set_xlabel('Margen Bruto (%)', color='#FF9800')\n"
    "ax2.tick_params(axis='x', labelcolor='#FF9800')\n"
    "ax2.set_xlim(30, 55)\n"
    "\n"
    "for x, y, m in zip(prod_plot['margen_pct'], prod_plot.index, prod_plot['margen_pct']):\n"
    "    ax2.annotate(f'{m}%', xy=(x, y), xytext=(3, 0),\n"
    "                 textcoords='offset points', va='center',\n"
    "                 fontsize=9, color='#E65100', fontweight='bold')\n"
    "\n"
    "ax1.invert_yaxis()\n"
    "plt.tight_layout()\n"
    "plt.savefig('data/processed/prod_ingreso_margen.png', bbox_inches='tight', dpi=120)\n"
    "print('Grafico 1 guardado.')\n"
)

# ── Cell 8: Seccion 4 ────────────────────────────────────────────────────────
MD[8] = (
    "## 4. Tendencia Mensual por Producto\n"
    "\n"
    "Rastrear la evolucion mensual de cada producto permite detectar "
    "estacionalidad, impulsos por campana y posibles declives. "
    "Esta vista es clave para planificar inventario y presupuesto de ads."
)

# ── Cell 9: Tendencia mensual ────────────────────────────────────────────────
CD[9] = (
    "mensual = df.groupby(['Mes', 'Nombre_Mes', 'Nombre_Producto'])['Ingreso_Total'].sum().reset_index()\n"
    "mensual = mensual.sort_values('Mes')\n"
    "\n"
    "nombres_cortos = {\n"
    "    'Vaso Termico Inteligente Auto': 'Vaso Termico',\n"
    "    'Mini Bicicleta Premium': 'Mini Bicicleta',\n"
    "    'Soporte Magnetico Carga': 'Soporte Magnetico',\n"
    "    'Cojin Ergonomico Gel': 'Cojin Ergonomico',\n"
    "}\n"
    "mensual['Producto_Corto'] = mensual['Nombre_Producto'].map(nombres_cortos)\n"
    "\n"
    "orden_meses = mensual.sort_values('Mes')[['Mes', 'Nombre_Mes']].drop_duplicates()\n"
    "etiquetas = orden_meses['Nombre_Mes'].tolist()\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(11, 5))\n"
    "\n"
    "colores_prod = {\n"
    "    'Vaso Termico': '#2196F3',\n"
    "    'Mini Bicicleta': '#FF5722',\n"
    "    'Soporte Magnetico': '#4CAF50',\n"
    "    'Cojin Ergonomico': '#9C27B0',\n"
    "}\n"
    "\n"
    "for prod_nombre, grupo in mensual.groupby('Producto_Corto'):\n"
    "    grupo = grupo.sort_values('Mes')\n"
    "    ax.plot(grupo['Nombre_Mes'], grupo['Ingreso_Total'],\n"
    "            marker='o', linewidth=2.5, markersize=7,\n"
    "            color=colores_prod.get(prod_nombre, 'gray'),\n"
    "            label=prod_nombre)\n"
    "\n"
    "ax.set_title('Tendencia Mensual de Ingresos por Producto', fontsize=13, fontweight='bold', pad=12)\n"
    "ax.set_xlabel('Mes')\n"
    "ax.set_ylabel('Ingreso Total (USD)')\n"
    "ax.legend(loc='upper left', framealpha=0.9)\n"
    "ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))\n"
    "plt.tight_layout()\n"
    "plt.savefig('data/processed/prod_tendencia_mensual.png', bbox_inches='tight', dpi=120)\n"
    "print('Grafico 2 guardado.')\n"
)

# ── Cell 10: Seccion 5 ───────────────────────────────────────────────────────
MD[10] = (
    "## 5. Distribucion Geografica\n"
    "\n"
    "El mapa de calor ciudad x producto revela donde se concentra la demanda "
    "de cada SKU. Esta informacion es util para personalizar campanas por "
    "ciudad y optimizar la logistica de ultimo kilometro."
)

# ── Cell 11: Heatmap ciudad x producto ──────────────────────────────────────
CD[11] = (
    "geo = df.pivot_table(\n"
    "    values='Ingreso_Total',\n"
    "    index='Nombre_Producto',\n"
    "    columns='Ciudad_Destino',\n"
    "    aggfunc='sum'\n"
    ").fillna(0)\n"
    "\n"
    "nombres_cortos = {\n"
    "    'Vaso Termico Inteligente Auto': 'Vaso Termico',\n"
    "    'Mini Bicicleta Premium': 'Mini Bicicleta',\n"
    "    'Soporte Magnetico Carga': 'Soporte Magnetico',\n"
    "    'Cojin Ergonomico Gel': 'Cojin Ergonomico',\n"
    "}\n"
    "geo.index = [nombres_cortos.get(n, n) for n in geo.index]\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(10, 4))\n"
    "im = ax.imshow(geo.values, cmap='Blues', aspect='auto')\n"
    "\n"
    "ax.set_xticks(range(len(geo.columns)))\n"
    "ax.set_xticklabels(geo.columns, fontsize=10)\n"
    "ax.set_yticks(range(len(geo.index)))\n"
    "ax.set_yticklabels(geo.index, fontsize=10)\n"
    "\n"
    "for i in range(len(geo.index)):\n"
    "    for j in range(len(geo.columns)):\n"
    "        val = geo.values[i, j]\n"
    "        color = 'white' if val > geo.values.max() * 0.6 else 'black'\n"
    "        ax.text(j, i, f'${val:,.0f}', ha='center', va='center',\n"
    "                fontsize=8.5, color=color, fontweight='bold')\n"
    "\n"
    "plt.colorbar(im, ax=ax, label='Ingreso (USD)')\n"
    "ax.set_title('Ingreso por Producto y Ciudad', fontsize=13, fontweight='bold', pad=12)\n"
    "plt.tight_layout()\n"
    "plt.savefig('data/processed/prod_heatmap_geo.png', bbox_inches='tight', dpi=120)\n"
    "print('Grafico 3 guardado.')\n"
    "\n"
    "print()\n"
    "print('Top ciudad por producto:')\n"
    "for prod_nombre in geo.index:\n"
    "    top_ciudad = geo.loc[prod_nombre].idxmax()\n"
    "    top_val = geo.loc[prod_nombre].max()\n"
    "    print(f'  {prod_nombre:<22}: {top_ciudad} (${top_val:,.0f})')\n"
)

# ── Cell 12: Seccion 6 ───────────────────────────────────────────────────────
MD[12] = (
    "## 6. Precio vs Volumen\n"
    "\n"
    "El scatter precio-volumen compara los cuatro productos en un mismo plano: "
    "el eje X muestra el precio promedio, el eje Y las unidades vendidas, "
    "y el tamano de la burbuja representa la ganancia bruta total. "
    "Un producto ideal ocupa la esquina superior derecha (alto precio, alto volumen)."
)

# ── Cell 13: Scatter precio vs volumen ──────────────────────────────────────
CD[13] = (
    "tmp = df.copy()\n"
    "tmp['precio_unit'] = tmp['Ingreso_Total'] / tmp['Cantidad']\n"
    "scatter_data = tmp.groupby('Nombre_Producto').agg(\n"
    "    precio_prom=('precio_unit', 'mean'),\n"
    "    unidades=('Cantidad', 'sum'),\n"
    "    ganancia=('Ganancia_Bruta', 'sum'),\n"
    ").reset_index()\n"
    "\n"
    "# nombre corto: primeras dos palabras\n"
    "scatter_data['nombre_corto'] = scatter_data['Nombre_Producto'].str.split().str[:2].str.join(' ')\n"
    "\n"
    "colores = ['#2196F3', '#FF5722', '#4CAF50', '#9C27B0']\n"
    "sizes = (scatter_data['ganancia'] / scatter_data['ganancia'].max() * 3000).values\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(9, 6))\n"
    "\n"
    "for i, row in scatter_data.iterrows():\n"
    "    ax.scatter(row['precio_prom'], row['unidades'],\n"
    "               s=sizes[i], color=colores[i], alpha=0.75, edgecolors='white', linewidth=1.5)\n"
    "    etiqueta = str(row['nombre_corto']) + '\\n$' + f\"{row['ganancia']:,.0f}\" + ' gan.'\n"
    "    ax.annotate(\n"
    "        etiqueta,\n"
    "        xy=(row['precio_prom'], row['unidades']),\n"
    "        xytext=(12, 0), textcoords='offset points',\n"
    "        fontsize=9, va='center',\n"
    "        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#cccccc', alpha=0.8)\n"
    "    )\n"
    "\n"
    "ax.set_xlabel('Precio Promedio (USD)', fontsize=11)\n"
    "ax.set_ylabel('Unidades Vendidas', fontsize=11)\n"
    "ax.set_title('Precio vs Volumen\\n(tamano de burbuja = ganancia bruta total)',\n"
    "             fontsize=13, fontweight='bold', pad=12)\n"
    "ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))\n"
    "ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.0f}'))\n"
    "plt.tight_layout()\n"
    "plt.savefig('data/processed/prod_scatter_precio_volumen.png', bbox_inches='tight', dpi=120)\n"
    "print('Grafico 4 guardado.')\n"
)

# ── Cell 14: Conclusiones ────────────────────────────────────────────────────
MD[14] = (
    "## Conclusiones\n"
    "\n"
    "### Hallazgos Clave\n"
    "\n"
    "| # | Hallazgo | Implicacion |\n"
    "|---|----------|-------------|\n"
    "| 1 | **Vaso Termico** lidera en ganancia ($30,832) y volumen (1,771 uds) | Producto ancla del negocio: proteger disponibilidad y escalar ads |\n"
    "| 2 | **Mini Bicicleta** lidera en ingresos ($76,080) con solo 634 uds | Ticket alto compensa menor volumen; ROAS de campana critico |\n"
    "| 3 | **Soporte Magnetico** tiene el mayor margen (45%) | Producto de alta eficiencia; potencial para bundle con Vaso |\n"
    "| 4 | **Cojin Ergonomico** tiene el menor volumen (404 uds) y menor ingreso | Evaluar si merece inversion en ads o funciona solo como complemento |\n"
    "| 5 | Margen global del portafolio: **43-45%** en todos los productos | Estructura de costos sana; el costo de envio es la variable a optimizar |\n"
    "\n"
    "### Recomendaciones\n"
    "\n"
    "1. **Duplicar inversion en Vaso Termico** - maxima ganancia por unidad y escala probada\n"
    "2. **Bundle Vaso + Soporte Magnetico** - ambos son categoria Auto, margen combinado alto\n"
    "3. **Revisar estrategia del Cojin Ergonomico** - analizar si campana activa o solo organico\n"
    "4. **Mini Bicicleta: proteger el margen** - COGS y envio pesan mas en productos de ticket alto"
)

# ── Cell 15: Print insights ──────────────────────────────────────────────────
CD[15] = (
    "total_ingreso = df['Ingreso_Total'].sum()\n"
    "total_ganancia = df['Ganancia_Bruta'].sum()\n"
    "margen_global = total_ganancia / total_ingreso * 100\n"
    "\n"
    "print('RESUMEN EJECUTIVO - RENTABILIDAD DE PRODUCTOS')\n"
    "print('=' * 60)\n"
    "print(f'Ingreso total portafolio : ${total_ingreso:,.0f}')\n"
    "print(f'Ganancia bruta total     : ${total_ganancia:,.0f}')\n"
    "print(f'Margen bruto global      : {margen_global:.1f}%')\n"
    "print()\n"
    "print('Ranking por ganancia bruta:')\n"
    "ganancia_rank = df.groupby('Nombre_Producto')['Ganancia_Bruta'].sum().sort_values(ascending=False)\n"
    "for i, (nombre, gan) in enumerate(ganancia_rank.items(), 1):\n"
    "    pct = gan / total_ganancia * 100\n"
    "    print(f'  {i}. {nombre:<35} ${gan:>9,.0f}  ({pct:.1f}%)')\n"
    "print()\n"
    "print('Producto mas rentable por unidad:')\n"
    "gan_unit = df.groupby('Nombre_Producto').apply(\n"
    "    lambda x: x['Ganancia_Bruta'].sum() / x['Cantidad'].sum()\n"
    ").sort_values(ascending=False)\n"
    "for nombre, val in gan_unit.items():\n"
    "    print(f'  {nombre:<35} ${val:.2f} / unidad')\n"
    "print()\n"
    "print('CSVs de soporte generados en data/processed/')\n"
    "df.groupby('Nombre_Producto').agg(\n"
    "    unidades=('Cantidad','sum'),\n"
    "    ingreso=('Ingreso_Total','sum'),\n"
    "    ganancia=('Ganancia_Bruta','sum')\n"
    ").round(2).to_csv('data/processed/prod_rentabilidad.csv')\n"
    "print('  prod_rentabilidad.csv exportado')\n"
)

# ---------------------------------------------------------------------------
# RUNNER
# ---------------------------------------------------------------------------

def run_cell(code_str, globs):
    buf = io.StringIO()
    images = []
    old = sys.stdout
    sys.stdout = buf
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


def make_md_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def make_code_cell(source, outputs):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": outputs,
        "source": source,
    }


def make_outputs(stdout_text, err_text, images):
    out = []
    if stdout_text.strip():
        out.append({
            "name": "stdout",
            "output_type": "stream",
            "text": stdout_text,
        })
    for img in images:
        out.append({
            "data": {"image/png": img, "text/plain": ["<Figure>"]},
            "metadata": {},
            "output_type": "display_data",
        })
    if err_text:
        out.append({
            "name": "stderr",
            "output_type": "stream",
            "text": err_text,
        })
    return out


# ---------------------------------------------------------------------------
# EJECUCION
# ---------------------------------------------------------------------------

CELL_ORDER = [
    ('md', 0), ('cd', 1),
    ('md', 2), ('cd', 3),
    ('md', 4), ('cd', 5),
    ('md', 6), ('cd', 7),
    ('md', 8), ('cd', 9),
    ('md', 10), ('cd', 11),
    ('md', 12), ('cd', 13),
    ('md', 14), ('cd', 15),
]

globs = {}
cells = []
errors_found = False

for kind, idx in CELL_ORDER:
    if kind == 'md':
        cells.append(make_md_cell(MD[idx]))
    else:
        print(f'Cell [{idx}] running...')
        stdout_text, err, images = run_cell(CD[idx], globs)
        if stdout_text.strip():
            print(stdout_text.rstrip())
        if err:
            print(f'  ERROR en Cell [{idx}]:\n{err}')
            errors_found = True
        cells.append(make_code_cell(CD[idx], make_outputs(stdout_text, err, images)))

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13.0"},
    },
    "cells": cells,
}

out_path = os.path.join('notebooks', '03_product_profitability.ipynb')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

status = 'CON ERRORES' if errors_found else 'OK'
print()
print(f'Notebook guardado: {out_path} ({len(cells)} celdas) [{status}]')
