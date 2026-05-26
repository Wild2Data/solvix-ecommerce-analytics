# Solvix E-commerce Analytics

End-to-end analytics project for **Solvix**, a fictional Colombian dropshipping company.
Six months of sales data (Nov 2025 – Apr 2026) analyzed with Python, SQL Server, and Power BI.

---

## Objective

Identify the most profitable products, understand customer behavior through RFM segmentation,
and evaluate Meta Ads campaign efficiency to support data-driven decisions.

---

## Dataset

| File | Description | Records |
|------|-------------|---------|
| `solvix_ordenes_raw.csv` | Orders with revenue, cost, margin and shipping | 3,500 |
| `solvix_meta_ads_raw.csv` | Daily Meta Ads spend and attributed purchases | 360 |

**Period:** November 2025 – April 2026  
**Cities:** Bogota, Medellin, Cali, Barranquilla, Bucaramanga  
**Products:** 4 SKUs across 3 categories (Auto, Fitness, Oficina/Auto)

---

## Project Structure

```
solvix-ecommerce-analytics/
│
├── data/
│   ├── raw/                        # Original generated CSVs
│   └── processed/                  # Cleaned data + RFM outputs + charts
│
├── notebooks/
│   ├── 01_data_generation.ipynb    # Synthetic data generation
│   ├── 02_cleaning_eda.ipynb       # Data cleaning and exploratory analysis
│   ├── 03_product_profitability.ipynb  # Product revenue, margin and geo analysis
│   └── 04_rfm_segmentation.ipynb   # RFM customer segmentation model
│
├── sql/
│   ├── setup_database.py           # SQL Server database setup
│   └── queries/
│       ├── 01_ventas_mensuales.sql     # Monthly revenue trend
│       ├── 02_top_productos.sql        # Top products by margin
│       ├── 03_rendimiento_ads.sql      # ROAS and CPA by campaign
│       └── 04_comportamiento_clientes.sql  # Customer behavior metrics
│
├── dashboard/                      # Power BI .pbix and screenshots
├── README.md
└── requirements.txt
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python + Pandas | Data generation, cleaning, EDA, RFM segmentation |
| SQL Server (T-SQL) | Business metrics queries, ROAS analysis |
| Power BI | Interactive dashboard for stakeholders |
| Matplotlib | Exploratory and publication-quality charts |

---

## Key Findings

### Products
- **Vaso Termico** leads in profit ($30,832) and volume (1,771 units) — the anchor product
- **Mini Bicicleta** leads in revenue ($76,080) at $120 avg ticket with 39.9% margin
- **Soporte Magnetico** has the highest margin (45.0%) — best efficiency per unit
- Overall portfolio margin: **42.7%**

### RFM Customer Segmentation (1,404 unique customers)
- **Champions** (23.3% of customers) generate **49.8% of total revenue** ($93,473)
- **Champions + Leales** = 614 customers (43.7%) drive **68% of all revenue**
- **En Riesgo**: 91 customers with $15,187 recoverable through reactivation campaigns
- **Hibernando**: 212 customers reachable with low-cost push/email campaigns

### Meta Ads Performance
- **Campana_Vaso_Vertical**: ROAS 20.3x — ROI 782%
- **Campana_Bici_Carrusel**: ROAS 8.91x — ROI 265%
- Both campaigns above break-even (ROAS > 4x), with Vaso Vertical as the standout performer

---

## How to Run

```bash
git clone https://github.com/Wild2Data/solvix-ecommerce-analytics.git
cd solvix-ecommerce-analytics
pip install -r requirements.txt
```

Open notebooks in order starting with `01_data_generation.ipynb`.

For SQL queries: run `sql/setup_database.py` to create the SQL Server database,
then execute queries in `sql/queries/` using SSMS or Azure Data Studio.

---

## Author

**Williams Aguilera Leon**  
[LinkedIn](https://linkedin.com/in/wild2data) · [GitHub](https://github.com/Wild2Data)
