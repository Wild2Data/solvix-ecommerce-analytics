# Solvix E-commerce Analytics

Análisis de datos **sintéticos** de una tienda ficticia colombiana, de noviembre de 2025 a abril de 2026. El proyecto explora rentabilidad de productos, segmentos RFM y campañas Meta Ads con Python, SQL Server y un dashboard de Power BI.

## Resultados reproducibles

| Indicador | Resultado |
|---|---:|
| Órdenes raw (incluyen 35 duplicados inyectados) | 3,535 |
| Órdenes limpias | 3,494 |
| Clientes únicos | 1,648 |
| Ingresos | USD 191,476.48 |
| Ganancia después de COGS y envío | USD 95,495.39 |
| Margen sobre ingresos | 49.9% |

Estos resultados proceden de `scripts/regenerate_data.py` con semilla fija 2025. Los CSV en `data/raw/` y `data/processed/` son salidas de ese script. Los cuadernos `01` y `02` llaman y examinan ese mismo flujo; no generan otro conjunto distinto.

### Productos

- **Mini Bicicleta Premium:** USD 90,877.56 de ingresos, USD 51,704 de ganancia, 757 unidades; es el producto con mayor ganancia.
- **Vaso Térmico:** 1,465 unidades, el mayor volumen, y USD 25,650.92 de ganancia.
- **Soporte Magnético:** 1,218 unidades y margen de 39.7%.

### Clientes

La segmentación RFM usa como referencia el inicio del día posterior a la última orden. Así ninguna compra futura produce recencia negativa. Hay 371 clientes Champions y 358 Leales; juntos suman 729 clientes (44.2%) y USD 118,304.70 en ingresos (61.8%). Los 109 clientes En Riesgo registran USD 16,858.80 de ingresos históricos; esa cifra **no** representa ingresos recuperables garantizados.

### Publicidad

Los datos de campañas también son sintéticos. El gasto total limpio es USD 3,485.11 en Vaso Vertical y USD 5,236.58 en Bici Carrusel. La consulta `sql/queries/03_rendimiento_ads.sql` calcula ROAS uniendo gasto por campaña con ingresos clasificados por fuente. Es una estimación dentro de esta simulación, no prueba causal de ventas incrementales. Los conteos `Compras_Atribuidas` del archivo de Ads se generan separadamente de las órdenes, por lo que no deben presentarse como conciliados.

## Ejecutar

```bash
pip install -r requirements.txt
python -X utf8 scripts/regenerate_data.py
python -X utf8 scripts/run_products_notebook.py
python -X utf8 scripts/run_rfm_notebook.py
```

Abre los cuadernos `notebooks/01_data_generation.ipynb` y `02_cleaning_eda.ipynb` desde la raíz del repositorio o desde `notebooks/`. `03_product_profitability.ipynb` y `04_rfm_segmentation.ipynb` se reconstruyen con resultados ejecutados mediante sus respectivos scripts. Para SQL Server, configura la conexión de `sql/setup_database.py` y ejecuta después las consultas de `sql/queries/`.

## Estructura

- `scripts/`: generación, limpieza y construcción de cuadernos.
- `data/raw/`: CSV sintéticos con errores inyectados para practicar limpieza.
- `data/processed/`: CSV limpios, segmentos, métricas y gráficos derivados.
- `notebooks/`: generación, control de calidad, productos y RFM.
- `sql/`: carga y consultas de SQL Server.
- `dashboard/`: capturas y tema de Power BI. Las capturas pueden reflejar una versión anterior de los datos; verifica las cifras contra los CSV actuales antes de presentarlas.

## Autor

**Williams Aguilera León** · [LinkedIn](https://linkedin.com/in/wild2data) · [GitHub](https://github.com/Wild2Data)
