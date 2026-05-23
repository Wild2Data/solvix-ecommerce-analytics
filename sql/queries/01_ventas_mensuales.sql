-- ============================================================
-- 01 — Ventas mensuales
-- Ingreso, ganancia y volumen de órdenes por mes
-- Base: dbo.ordenes | Período: Nov 2025 – Abr 2026
-- ============================================================

USE solvix_analytics;

SELECT
    Mes,
    Nombre_Mes,
    COUNT(*)                        AS total_ordenes,
    SUM(Cantidad)                   AS unidades_vendidas,
    SUM(Ingreso_Total)              AS ingreso_total,
    SUM(COGS_Total)                 AS costo_mercancia,
    SUM(Costo_Envio)                AS costo_envio_total,
    SUM(Ganancia_Bruta)             AS ganancia_bruta,
    ROUND(
        SUM(Ganancia_Bruta) * 100.0
        / NULLIF(SUM(Ingreso_Total), 0), 2
    )                               AS margen_bruto_pct,
    ROUND(AVG(CAST(Ingreso_Total AS FLOAT)), 2)
                                    AS ticket_promedio
FROM dbo.ordenes
GROUP BY Mes, Nombre_Mes
ORDER BY Mes;
