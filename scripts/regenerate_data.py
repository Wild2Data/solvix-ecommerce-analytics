"""
Regenera datos raw (sucios) y procesados (limpios) para Solvix.
Ejecutar desde la raiz del proyecto: python -X utf8 scripts/regenerate_data.py

Cambios vs version anterior:
- Raw: solo columnas unitarias (sin calcular), sin columnas derivadas de tiempo
- Raw: nulls reales, duplicados, fechas inconsistentes, ciudades mal escritas
- Raw: precios variables (+-8%), pedidos de qty > 1, distribucion de ciudades realista
- Raw: tendencias de producto: Mini Bici declina Feb-Abr, Soporte crece
- Ads raw: dias pausados, gasto anomalo, clics en 0
- Processed: limpieza completa, columnas calculadas y de tiempo
"""
import os, sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(2025)
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# ---------------------------------------------------------------------------
# PARAMETROS
# ---------------------------------------------------------------------------
N_BASE   = 3500
START    = datetime(2025, 11, 1)
END      = datetime(2026, 4, 30)
N_DAYS   = (END - START).days + 1   # 181 dias

PRODUCTOS = {
    'P001': {'nombre': 'Vaso Termico Inteligente Auto', 'cat': 'Auto',        'precio': 39,  'cogs': 15, 'peso': 0.32},
    'P002': {'nombre': 'Mini Bicicleta Premium',        'cat': 'Fitness',     'precio': 120, 'cogs': 45, 'peso': 0.25},
    'P003': {'nombre': 'Soporte Magnetico Carga',       'cat': 'Oficina/Auto','precio': 24,  'cogs': 8,  'peso': 0.20},
    'P004': {'nombre': 'Cojin Ergonomico Gel',          'cat': 'Oficina/Auto','precio': 34,  'cogs': 12, 'peso': 0.23},
}

# Distribucion de ciudades realista (Bogota domina)
CIUDADES = {
    'Bogota':       {'w': 0.35, 'ship_base': 5.5,  'ship_std': 1.8},
    'Medellin':     {'w': 0.22, 'ship_base': 6.2,  'ship_std': 2.0},
    'Cali':         {'w': 0.20, 'ship_base': 6.8,  'ship_std': 2.2},
    'Barranquilla': {'w': 0.14, 'ship_base': 8.1,  'ship_std': 2.5},
    'Bucaramanga':  {'w': 0.09, 'ship_base': 9.4,  'ship_std': 3.0},
}

FUENTES = ['Campana_Vaso_Vertical', 'Campana_Bici_Carrusel', 'Organico_Instagram', 'Directo']

# Multiplicadores mensuales de demanda (estacionalidad)
MES_MULT = {11: 1.00, 12: 1.38, 1: 0.71, 2: 0.94, 3: 1.06, 4: 1.12}

# ---------------------------------------------------------------------------
# GENERACION DE FECHAS (con peso por mes y fin de semana)
# ---------------------------------------------------------------------------
print('Generando fechas...')
dias = [START + timedelta(days=i) for i in range(N_DAYS)]
pesos_dia = []
for d in dias:
    m_w = MES_MULT.get(d.month, 1.0)
    wd_w = 1.18 if d.weekday() >= 5 else 1.0  # fin de semana +18%
    pesos_dia.append(m_w * wd_w)

pesos_dia = np.array(pesos_dia) / sum(pesos_dia)
fechas_ordenes = np.random.choice(dias, size=N_BASE, p=pesos_dia)
fechas_ordenes = sorted(fechas_ordenes)

# Agregar hora aleatoria
def add_random_time(d):
    return d + timedelta(
        hours=int(np.random.randint(0, 24)),
        minutes=np.random.randint(0, 60),
        seconds=np.random.randint(0, 60)
    )

fechas_ordenes = [add_random_time(d) for d in fechas_ordenes]

# ---------------------------------------------------------------------------
# SELECCION DE PRODUCTOS (con tendencia temporal)
# ---------------------------------------------------------------------------
print('Asignando productos...')

def peso_producto_por_mes(mes):
    # P002 Mini Bici: declina desde febrero
    # P003 Soporte: crece desde enero
    base = {'P001': 0.38, 'P002': 0.28, 'P003': 0.24, 'P004': 0.10}
    decline_bici  = max(0, (mes - 1) * 0.025) if mes >= 2 else 0
    growth_soport = max(0, (mes - 1) * 0.020) if mes >= 1 else 0
    w = {
        'P001': base['P001'],
        'P002': max(0.12, base['P002'] - decline_bici),
        'P003': min(0.34, base['P003'] + growth_soport),
        'P004': base['P004'],
    }
    total = sum(w.values())
    return {k: v/total for k, v in w.items()}

prod_ids = []
for fecha in fechas_ordenes:
    mes = fecha.month
    w = peso_producto_por_mes(mes)
    pid = np.random.choice(list(w.keys()), p=list(w.values()))
    prod_ids.append(pid)

# ---------------------------------------------------------------------------
# CANTIDAD (mayoria 1, algunos pedidos de 2-4)
# ---------------------------------------------------------------------------
cantidades = np.random.choice([1, 2, 3, 4], size=N_BASE, p=[0.91, 0.06, 0.02, 0.01])

# ---------------------------------------------------------------------------
# CLIENTES
# ---------------------------------------------------------------------------
n_clientes = 1404
cliente_ids = [f'CLI-{np.random.randint(5000, 7000):04d}' for _ in range(N_BASE)]

# ---------------------------------------------------------------------------
# CIUDADES
# ---------------------------------------------------------------------------
nombres_ciudad = list(CIUDADES.keys())
pesos_ciudad = [CIUDADES[c]['w'] for c in nombres_ciudad]
ciudades = np.random.choice(nombres_ciudad, size=N_BASE, p=pesos_ciudad)

# ---------------------------------------------------------------------------
# FUENTE DE ADQUISICION (ligada al producto)
# ---------------------------------------------------------------------------
def fuente_por_producto(pid):
    if pid == 'P001':
        return np.random.choice(FUENTES, p=[0.35, 0.05, 0.40, 0.20])
    elif pid == 'P002':
        return np.random.choice(FUENTES, p=[0.05, 0.40, 0.35, 0.20])
    else:
        return np.random.choice(FUENTES, p=[0.15, 0.15, 0.45, 0.25])

fuentes = [fuente_por_producto(p) for p in prod_ids]

# ---------------------------------------------------------------------------
# PRECIOS CON VARIACION REALISTA (+-8%)
# ---------------------------------------------------------------------------
def precio_variable(pid, ciudad):
    base = PRODUCTOS[pid]['precio']
    variacion = np.random.uniform(-0.08, 0.08)
    precio = base * (1 + variacion)
    return round(precio, 2)

def cogs_variable(pid):
    base = PRODUCTOS[pid]['cogs']
    variacion = np.random.uniform(-0.05, 0.07)
    return round(base * (1 + variacion), 2)

def costo_envio(ciudad, cantidad):
    c = CIUDADES[ciudad]
    base = c['ship_base'] * (1 + (cantidad - 1) * 0.35)
    return round(max(3.0, np.random.normal(base, c['ship_std'])), 2)

precios   = [precio_variable(p, c) for p, c in zip(prod_ids, ciudades)]
cogs_unit = [cogs_variable(p) for p in prod_ids]
envios    = [costo_envio(c, q) for c, q in zip(ciudades, cantidades)]

# ---------------------------------------------------------------------------
# ESTADO DE ENVIO
# ---------------------------------------------------------------------------
estados = np.random.choice(
    ['Entregado', 'En transito', 'Retrasado', 'Devuelto'],
    size=N_BASE,
    p=[0.81, 0.10, 0.06, 0.03]
)

# ---------------------------------------------------------------------------
# CONSTRUCCION DEL DATAFRAME LIMPIO
# ---------------------------------------------------------------------------
print('Construyendo dataframe base...')
df_clean_base = pd.DataFrame({
    'ID_Orden':          [f'ORD-{1000+i}' for i in range(N_BASE)],
    'Fecha':             [f.strftime('%Y-%m-%d %H:%M:%S') for f in fechas_ordenes],
    'ID_Cliente':        cliente_ids,
    'ID_Producto':       prod_ids,
    'Nombre_Producto':   [PRODUCTOS[p]['nombre'] for p in prod_ids],
    'Categoria':         [PRODUCTOS[p]['cat']    for p in prod_ids],
    'Cantidad':          cantidades,
    'Precio_Unitario':   precios,
    'COGS_Unitario':     cogs_unit,
    'Costo_Envio':       envios,
    'Ciudad_Destino':    ciudades,
    'Fuente_Adquisicion':fuentes,
    'Estado_Envio':      estados,
})

# ---------------------------------------------------------------------------
# CREAR RAW SUCIO (copia del limpio + contaminaciones)
# ---------------------------------------------------------------------------
print('Aplicando suciedad al raw...')
df_raw = df_clean_base.copy()
n = len(df_raw)

# 1. NULLS en Ciudad_Destino (~2.7%)
idx_null_ciudad = np.random.choice(n, size=94, replace=False)
df_raw.loc[idx_null_ciudad, 'Ciudad_Destino'] = np.nan

# 2. NULLS en Fuente_Adquisicion (~1.9%)
idx_null_fuente = np.random.choice(
    [i for i in range(n) if i not in idx_null_ciudad], size=67, replace=False
)
df_raw.loc[idx_null_fuente, 'Fuente_Adquisicion'] = np.nan

# 3. NULLS en Costo_Envio (~1.4%)
idx_null_envio = np.random.choice(
    [i for i in range(n) if i not in list(idx_null_ciudad) + list(idx_null_fuente)],
    size=49, replace=False
)
df_raw.loc[idx_null_envio, 'Costo_Envio'] = np.nan

# 4. DUPLICADOS (~35 filas repetidas)
idx_dup = np.random.choice(n, size=35, replace=False)
duplicados = df_raw.iloc[idx_dup].copy()
df_raw = pd.concat([df_raw, duplicados], ignore_index=True)
df_raw = df_raw.sample(frac=1, random_state=42).reset_index(drop=True)

# 5. FECHAS CON FORMATO INCORRECTO (DD/MM/YYYY en ~22 filas)
idx_fecha_mal = np.random.choice(len(df_raw), size=22, replace=False)
for i in idx_fecha_mal:
    try:
        dt = datetime.strptime(df_raw.loc[i, 'Fecha'], '%Y-%m-%d %H:%M:%S')
        df_raw.loc[i, 'Fecha'] = dt.strftime('%d/%m/%Y %H:%M:%S')
    except Exception:
        pass

# 6. COSTO_ENVIO NEGATIVO (~14 filas, error de ingreso)
idx_envio_neg = np.random.choice(
    df_raw[df_raw['Costo_Envio'].notna()].index.tolist(), size=14, replace=False
)
df_raw.loc[idx_envio_neg, 'Costo_Envio'] = df_raw.loc[idx_envio_neg, 'Costo_Envio'] * -1

# 7. CIUDADES MAL ESCRITAS (variantes sin acento o en minuscula)
variantes_ciudad = {
    'Bogota':       ['bogota', 'BOGOTA', 'Bogota '],
    'Medellin':     ['medellin', 'MEDELLIN', 'Medellin '],
    'Cali':         ['cali', 'CALI'],
    'Barranquilla': ['barranquilla', 'BARRANQUILLA'],
    'Bucaramanga':  ['bucaramanga'],
}
idx_ciudad_mal = np.random.choice(
    df_raw[df_raw['Ciudad_Destino'].notna()].index.tolist(), size=19, replace=False
)
for i in idx_ciudad_mal:
    ciudad_actual = df_raw.loc[i, 'Ciudad_Destino']
    if ciudad_actual in variantes_ciudad:
        opciones = variantes_ciudad[ciudad_actual]
        df_raw.loc[i, 'Ciudad_Destino'] = np.random.choice(opciones)

# 8. ESPACIOS EN NOMBRE_PRODUCTO (~11 filas)
idx_espacios = np.random.choice(len(df_raw), size=11, replace=False)
df_raw.loc[idx_espacios, 'Nombre_Producto'] = df_raw.loc[idx_espacios, 'Nombre_Producto'] + ' '

# 9. PRECIO_UNITARIO en 0 (~6 filas, error de sistema)
idx_precio_cero = np.random.choice(len(df_raw), size=6, replace=False)
df_raw.loc[idx_precio_cero, 'Precio_Unitario'] = 0.0

print(f'  Filas raw          : {len(df_raw):,}')
print(f'  Nulls Ciudad       : {df_raw["Ciudad_Destino"].isna().sum()}')
print(f'  Nulls Fuente       : {df_raw["Fuente_Adquisicion"].isna().sum()}')
print(f'  Nulls Costo_Envio  : {df_raw["Costo_Envio"].isna().sum()}')
print(f'  Duplicados aprox.  : 35 filas inyectadas')
print(f'  Fechas mal formato : 22 filas (DD/MM/YYYY)')
print(f'  Costo_Envio negat. : {(df_raw["Costo_Envio"] < 0).sum()}')
print(f'  Precio 0           : {(df_raw["Precio_Unitario"] == 0).sum()}')

# ---------------------------------------------------------------------------
# GUARDAR RAW
# ---------------------------------------------------------------------------
df_raw.to_csv('data/raw/solvix_ordenes_raw.csv', index=False, encoding='utf-8-sig')
print('Guardado: data/raw/solvix_ordenes_raw.csv')

# ---------------------------------------------------------------------------
# LIMPIAR Y CONSTRUIR PROCESSED
# ---------------------------------------------------------------------------
print()
print('Limpiando datos...')
df = df_raw.copy()

# 1. Eliminar duplicados
antes = len(df)
df = df.drop_duplicates(subset='ID_Orden', keep='first')
print(f'  Duplicados eliminados: {antes - len(df)}')

# 2. Corregir fechas con formato DD/MM/YYYY
def parse_fecha(f):
    for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(str(f), fmt)
        except Exception:
            continue
    return pd.NaT

df['Fecha'] = df['Fecha'].apply(parse_fecha)
print(f'  Fechas convertidas. NaT: {df["Fecha"].isna().sum()}')

# 3. Estandarizar Ciudad_Destino
mapa_ciudades = {
    'bogota': 'Bogota', 'BOGOTA': 'Bogota', 'Bogota ': 'Bogota',
    'medellin': 'Medellin', 'MEDELLIN': 'Medellin', 'Medellin ': 'Medellin',
    'cali': 'Cali', 'CALI': 'Cali',
    'barranquilla': 'Barranquilla', 'BARRANQUILLA': 'Barranquilla',
    'bucaramanga': 'Bucaramanga',
}
df['Ciudad_Destino'] = df['Ciudad_Destino'].replace(mapa_ciudades)
moda_ciudad = df['Ciudad_Destino'].mode()[0]
df['Ciudad_Destino'] = df['Ciudad_Destino'].fillna(moda_ciudad)
print(f'  Ciudad estandarizada. Ciudades unicas: {df["Ciudad_Destino"].nunique()}')

# 4. Limpiar espacios en Nombre_Producto
df['Nombre_Producto'] = df['Nombre_Producto'].str.strip()

# 5. Costo_Envio: corregir negativos y llenar nulls
df['Costo_Envio'] = df['Costo_Envio'].abs()
mediana_envio = df.groupby('Ciudad_Destino')['Costo_Envio'].transform('median')
df['Costo_Envio'] = df['Costo_Envio'].fillna(mediana_envio).round(2)
print(f'  Costo_Envio limpio. Nulls restantes: {df["Costo_Envio"].isna().sum()}')

# 6. Fuente_Adquisicion: llenar nulls con moda por producto
moda_fuente = df.groupby('ID_Producto')['Fuente_Adquisicion'].transform(
    lambda x: x.mode()[0] if x.notna().any() else 'Organico_Instagram'
)
df['Fuente_Adquisicion'] = df['Fuente_Adquisicion'].fillna(moda_fuente)

# 7. Eliminar filas con Precio_Unitario == 0
antes = len(df)
df = df[df['Precio_Unitario'] > 0]
print(f'  Filas con precio 0 eliminadas: {antes - len(df)}')

# 8. Calcular columnas derivadas
df['Ingreso_Total']  = (df['Precio_Unitario'] * df['Cantidad']).round(2)
df['COGS_Total']     = (df['COGS_Unitario']   * df['Cantidad']).round(2)
df['Ganancia_Bruta'] = (df['Ingreso_Total'] - df['COGS_Total'] - df['Costo_Envio']).round(2)

# 9. Columnas de tiempo
df['Mes']        = df['Fecha'].dt.month
df['Nombre_Mes'] = df['Fecha'].dt.strftime('%B')
df['Dia_Semana'] = df['Fecha'].dt.strftime('%A')
df['Semana_Anio']= df['Fecha'].dt.isocalendar().week.astype(int)

# Reordenar columnas (igual que la version anterior para no romper notebooks)
cols_procesado = [
    'ID_Orden', 'Fecha', 'ID_Cliente', 'ID_Producto', 'Nombre_Producto',
    'Categoria', 'Cantidad', 'Ingreso_Total', 'COGS_Total', 'Costo_Envio',
    'Ganancia_Bruta', 'Ciudad_Destino', 'Fuente_Adquisicion', 'Estado_Envio',
    'Mes', 'Nombre_Mes', 'Dia_Semana', 'Semana_Anio'
]
df = df[cols_procesado]

print()
print('PROCESADO - Resumen:')
print(f'  Ordenes limpias    : {len(df):,}')
print(f'  Clientes unicos    : {df["ID_Cliente"].nunique():,}')
print(f'  Ingreso total      : ${df["Ingreso_Total"].sum():,.0f}')
print(f'  Ganancia bruta     : ${df["Ganancia_Bruta"].sum():,.0f}')
print(f'  Margen global      : {df["Ganancia_Bruta"].sum()/df["Ingreso_Total"].sum()*100:.1f}%')
print()
print('  Distribucion ciudades:')
print(df['Ciudad_Destino'].value_counts(normalize=True).mul(100).round(1).to_string())

df.to_csv('data/processed/solvix_ordenes_clean.csv', index=False, encoding='utf-8-sig')
print()
print('Guardado: data/processed/solvix_ordenes_clean.csv')

# ---------------------------------------------------------------------------
# META ADS - REGENERAR CON SUCIEDAD
# ---------------------------------------------------------------------------
print()
print('Generando Meta Ads data...')

campanas = ['Campana_Vaso_Vertical', 'Campana_Bici_Carrusel']
ads_rows = []
fecha_actual = START

while fecha_actual <= END:
    for campana in campanas:
        mes = fecha_actual.month
        mes_factor = MES_MULT.get(mes, 1.0)

        if campana == 'Campana_Vaso_Vertical':
            gasto_base = 18.0
            clics_base = 260
            conv_rate  = 0.024
        else:
            gasto_base = 28.0
            clics_base = 95
            conv_rate  = 0.022

        gasto = round(np.random.normal(gasto_base * mes_factor, gasto_base * 0.18), 2)
        gasto = max(0.0, gasto)
        clics = max(0, int(np.random.normal(clics_base * mes_factor, clics_base * 0.15)))
        compras = max(0, np.random.binomial(clics, conv_rate)) if clics > 0 else 0

        ads_rows.append({
            'Fecha':              fecha_actual.strftime('%Y-%m-%d'),
            'Nombre_Campana':     campana,
            'Gasto_Diario_USD':   gasto,
            'Clics':              clics,
            'Compras_Atribuidas': compras,
        })
    fecha_actual += timedelta(days=1)

df_ads = pd.DataFrame(ads_rows)

# --- SUCIEDAD ADS ---

# 1. Dias pausados (~12 dias con NaN en gasto)
idx_pausados = np.random.choice(len(df_ads), size=12, replace=False)
df_ads.loc[idx_pausados, 'Gasto_Diario_USD'] = np.nan
df_ads.loc[idx_pausados, 'Clics'] = 0
df_ads.loc[idx_pausados, 'Compras_Atribuidas'] = 0

# 2. Dias con gasto anomalo (error de presupuesto, ~5 dias, 2.5x normal)
idx_anomalia = np.random.choice(
    df_ads[df_ads['Gasto_Diario_USD'].notna()].index.tolist(), size=5, replace=False
)
df_ads.loc[idx_anomalia, 'Gasto_Diario_USD'] = (
    df_ads.loc[idx_anomalia, 'Gasto_Diario_USD'] * 2.5
).round(2)

# 3. Clics en 0 con gasto positivo (falla de tracking, ~8 filas)
idx_sin_clics = np.random.choice(
    df_ads[df_ads['Gasto_Diario_USD'].notna() & (df_ads['Clics'] > 0)].index.tolist(),
    size=8, replace=False
)
df_ads.loc[idx_sin_clics, 'Clics'] = 0

# 4. Nombre de campana con typo (~5 filas)
typos = {
    'Campana_Vaso_Vertical':  'Campana_Vaso_Vertcal',
    'Campana_Bici_Carrusel': 'campana_bici_carrusel',
}
idx_typo = np.random.choice(len(df_ads), size=5, replace=False)
for i in idx_typo:
    nombre = df_ads.loc[i, 'Nombre_Campana']
    if nombre in typos:
        df_ads.loc[i, 'Nombre_Campana'] = typos[nombre]

print(f'  Filas ads raw      : {len(df_ads)}')
print(f'  Nulls Gasto        : {df_ads["Gasto_Diario_USD"].isna().sum()}')
print(f'  Dias clics=0       : {(df_ads["Clics"]==0).sum()}')
print(f'  Typos nombre       : 5 inyectados')

df_ads.to_csv('data/raw/solvix_meta_ads_raw.csv', index=False, encoding='utf-8-sig')
print('Guardado: data/raw/solvix_meta_ads_raw.csv')

# --- ADS LIMPIO ---
df_ads_clean = df_ads.copy()
df_ads_clean['Nombre_Campana'] = df_ads_clean['Nombre_Campana'].str.strip().str.lower()
nombre_map = {
    'campana_vaso_vertical':  'Campana_Vaso_Vertical',
    'campana_vaso_vertcal':   'Campana_Vaso_Vertical',
    'campana_bici_carrusel':  'Campana_Bici_Carrusel',
}
df_ads_clean['Nombre_Campana'] = df_ads_clean['Nombre_Campana'].map(nombre_map).fillna(
    df_ads_clean['Nombre_Campana']
)
mediana_gasto_camp = df_ads_clean.groupby('Nombre_Campana')['Gasto_Diario_USD'].transform('median')
df_ads_clean['Gasto_Diario_USD'] = df_ads_clean['Gasto_Diario_USD'].fillna(mediana_gasto_camp).round(2)
df_ads_clean.to_csv('data/processed/solvix_ads_clean.csv', index=False, encoding='utf-8-sig')
print('Guardado: data/processed/solvix_ads_clean.csv')

print()
print('Regeneracion completa.')
