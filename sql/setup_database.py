"""
Setup: crea la base de datos solvix_analytics en SQL Server
y carga las tablas desde los archivos CSV procesados.
"""
import pyodbc
import pandas as pd
import os

SERVER   = r'localhost\SQLEXPRESS'
DB       = 'solvix_analytics'
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

def get_conn(database='master'):
    return pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={SERVER};DATABASE={database};Trusted_Connection=yes;',
        autocommit=True
    )

# ── 1. Crear la base de datos ──────────────────────────────────────────────────
print("Creando base de datos...")
with get_conn() as conn:
    cur = conn.cursor()
    cur.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{DB}') CREATE DATABASE {DB}")
    print(f"  Base de datos '{DB}' lista")

# ── 2. Crear tablas ────────────────────────────────────────────────────────────
CREATE_ORDENES = """
IF OBJECT_ID('dbo.ordenes', 'U') IS NOT NULL DROP TABLE dbo.ordenes;
CREATE TABLE dbo.ordenes (
    ID_Orden           NVARCHAR(20)   NOT NULL PRIMARY KEY,
    Fecha              DATETIME2      NOT NULL,
    ID_Cliente         NVARCHAR(20)   NOT NULL,
    ID_Producto        NVARCHAR(20)   NOT NULL,
    Nombre_Producto    NVARCHAR(100)  NOT NULL,
    Categoria          NVARCHAR(50)   NOT NULL,
    Cantidad           INT            NOT NULL,
    Ingreso_Total      INT            NOT NULL,
    COGS_Total         INT            NOT NULL,
    Costo_Envio        DECIMAL(10,2)  NOT NULL,
    Ganancia_Bruta     DECIMAL(10,2)  NOT NULL,
    Ciudad_Destino     NVARCHAR(50)   NOT NULL,
    Fuente_Adquisicion NVARCHAR(50)   NOT NULL,
    Estado_Envio       NVARCHAR(30)   NOT NULL,
    Mes                INT            NOT NULL,
    Nombre_Mes         NVARCHAR(20)   NOT NULL,
    Dia_Semana         NVARCHAR(20)   NOT NULL,
    Semana_Anio        INT            NOT NULL
);
"""

CREATE_ADS = """
IF OBJECT_ID('dbo.meta_ads', 'U') IS NOT NULL DROP TABLE dbo.meta_ads;
CREATE TABLE dbo.meta_ads (
    Fecha                DATETIME2     NOT NULL,
    Nombre_Campana       NVARCHAR(100) NOT NULL,
    Gasto_Diario_USD     DECIMAL(10,2) NOT NULL,
    Clics                INT           NOT NULL,
    Compras_Atribuidas   INT           NOT NULL
);
"""

print("Creando tablas...")
with get_conn(DB) as conn:
    cur = conn.cursor()
    cur.execute(CREATE_ORDENES)
    cur.execute(CREATE_ADS)
    print("  Tablas 'ordenes' y 'meta_ads' listas")

# ── 3. Cargar datos ────────────────────────────────────────────────────────────
print("Cargando datos...")

df_ordenes = pd.read_csv(os.path.join(DATA_DIR, 'solvix_ordenes_clean.csv'))
df_ads     = pd.read_csv(os.path.join(DATA_DIR, 'solvix_ads_clean.csv'))

with get_conn(DB) as conn:
    cur = conn.cursor()

    # Ordenes
    rows_o = [tuple(r) for r in df_ordenes.itertuples(index=False)]
    placeholders = ','.join(['?'] * len(df_ordenes.columns))
    cur.executemany(f"INSERT INTO dbo.ordenes VALUES ({placeholders})", rows_o)
    conn.commit()
    print(f"  ordenes:   {len(rows_o):,} filas insertadas")

    # Meta Ads (renombrar columna con tilde para SQL)
    df_ads = df_ads.rename(columns={'Nombre_Campaña': 'Nombre_Campana'})
    rows_a = [tuple(r) for r in df_ads.itertuples(index=False)]
    placeholders = ','.join(['?'] * len(df_ads.columns))
    cur.executemany(f"INSERT INTO dbo.meta_ads VALUES ({placeholders})", rows_a)
    conn.commit()
    print(f"  meta_ads:  {len(rows_a):,} filas insertadas")

# ── 4. Verificacion final ──────────────────────────────────────────────────────
print("\nVerificacion:")
with get_conn(DB) as conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dbo.ordenes")
    print(f"  dbo.ordenes   -> {cur.fetchone()[0]:,} filas")
    cur.execute("SELECT COUNT(*) FROM dbo.meta_ads")
    print(f"  dbo.meta_ads  -> {cur.fetchone()[0]:,} filas")
    cur.execute("SELECT MIN(Fecha), MAX(Fecha) FROM dbo.ordenes")
    row = cur.fetchone()
    print(f"  Rango fechas  -> {row[0].date()} al {row[1].date()}")

print("\nSetup completado. Base de datos lista para consultas.")
