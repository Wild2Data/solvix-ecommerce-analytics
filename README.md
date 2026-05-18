# Solvix E-commerce Analytics

End-to-end analysis of 6 months of sales data and Meta Ads campaigns for Solvix,
a Colombian dropshipping company operating in 5 major cities.

---

## Objective

Identify the most profitable products, understand customer behavior,
and evaluate marketing campaign efficiency to support data-driven decisions.

---

## Dataset

| File | Description | Records |
|------|-------------|---------|
| `solvix_ordenes_raw.csv` | Orders with revenue, cost, margin and shipping | 3,500 |
| `solvix_meta_ads_raw.csv` | Daily Meta Ads spend and attributed purchases | 360 |

**Period:** November 2025 – April 2026  
**Cities:** Bogotá, Medellín, Cali, Barranquilla, Bucaramanga

---

## Project Structure

```
solvix-ecommerce-analytics/
│
├── data/
│   ├── raw/          # Original generated CSVs
│   └── processed/    # Cleaned data ready for analysis
│
├── notebooks/
│   ├── 01_data_generation.ipynb
│   ├── 02_cleaning_eda.ipynb
│   ├── 03_product_profitability.ipynb
│   ├── 04_rfm_segmentation.ipynb
│   └── 05_marketing_roas.ipynb
│
├── sql/              # Business metrics queries (SQLite)
├── dashboard/        # Power BI screenshots and .pbix file
│
├── README.md
└── requirements.txt
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python + Pandas | Data generation, cleaning, EDA, RFM segmentation |
| SQL (SQLite) | Business metrics queries |
| Power BI | Interactive dashboard for stakeholders |
| Matplotlib / Seaborn | Exploratory visualizations |

---

## Key Findings

> Work in progress — results will be updated as analysis is completed.

---

## How to Run

```bash
git clone https://github.com/YOUR_USERNAME/solvix-ecommerce-analytics.git
cd solvix-ecommerce-analytics
pip install -r requirements.txt
```

Open the notebooks in order starting with `01_data_generation.ipynb`.

---

## Author

**[Tu nombre]**  
[LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/tu-usuario)
