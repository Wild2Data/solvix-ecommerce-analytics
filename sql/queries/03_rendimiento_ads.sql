-- ============================================================
-- 03 — Rendimiento de campañas Meta Ads
-- ROAS, CPA y eficiencia por campaña
-- ============================================================

USE solvix_analytics;

-- ── Métricas por campaña (período completo) ─────────────────
SELECT
    Nombre_Campana,
    COUNT(*)                            AS dias_activos,
    SUM(Gasto_Diario_USD)               AS gasto_total_usd,
    SUM(Clics)                          AS clics_totales,
    SUM(Compras_Atribuidas)             AS compras_totales,
    ROUND(
        SUM(Gasto_Diario_USD)
        / NULLIF(SUM(Clics), 0), 3
    )                                   AS cpc_usd,
    ROUND(
        SUM(Gasto_Diario_USD)
        / NULLIF(SUM(Compras_Atribuidas), 0), 2
    )                                   AS cpa_usd,
    ROUND(
        CAST(SUM(Compras_Atribuidas) AS FLOAT)
        / NULLIF(SUM(Clics), 0) * 100, 2
    )                                   AS tasa_conversion_pct
FROM dbo.meta_ads
GROUP BY Nombre_Campana
ORDER BY gasto_total_usd DESC;


-- ── ROAS: cruzar gasto ads con ingresos atribuidos por fuente ─
-- CTE para pre-agregar cada fuente antes del JOIN y evitar
-- multiplicar el gasto por número de órdenes (fan-out trap)
WITH gasto_campana AS (
    SELECT Nombre_Campana,
           SUM(Gasto_Diario_USD) AS gasto_usd
    FROM dbo.meta_ads
    GROUP BY Nombre_Campana
),
ingresos_campana AS (
    SELECT Fuente_Adquisicion AS Nombre_Campana,
           SUM(Ingreso_Total)  AS ingreso_atribuido,
           SUM(Ganancia_Bruta) AS ganancia_atribuida
    FROM dbo.ordenes
    GROUP BY Fuente_Adquisicion
)
SELECT
    g.Nombre_Campana,
    g.gasto_usd,
    i.ingreso_atribuido,
    ROUND(
        CAST(i.ingreso_atribuido AS FLOAT)
        / NULLIF(g.gasto_usd, 0), 2
    )                                   AS roas,
    i.ganancia_atribuida,
    ROUND(
        (i.ganancia_atribuida - g.gasto_usd)
        / NULLIF(g.gasto_usd, 0) * 100, 2
    )                                   AS roi_pct
FROM gasto_campana g
LEFT JOIN ingresos_campana i
    ON i.Nombre_Campana = g.Nombre_Campana
ORDER BY roas DESC;
