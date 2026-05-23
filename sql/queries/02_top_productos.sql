-- ============================================================
-- 02 — Top productos por ingreso y margen
-- Identifica los productos más rentables vs. más vendidos
-- ============================================================

USE solvix_analytics;

SELECT
    ID_Producto,
    Nombre_Producto,
    Categoria,
    COUNT(*)                        AS total_ordenes,
    SUM(Cantidad)                   AS unidades_vendidas,
    SUM(Ingreso_Total)              AS ingreso_total,
    SUM(Ganancia_Bruta)             AS ganancia_bruta,
    ROUND(
        SUM(Ganancia_Bruta) * 100.0
        / NULLIF(SUM(Ingreso_Total), 0), 2
    )                               AS margen_pct,
    ROUND(AVG(CAST(Ingreso_Total AS FLOAT)), 2)
                                    AS ticket_promedio
FROM dbo.ordenes
GROUP BY ID_Producto, Nombre_Producto, Categoria
ORDER BY ingreso_total DESC;


-- ── Desglose por categoría ──────────────────────────────────
SELECT
    Categoria,
    COUNT(DISTINCT ID_Producto)     AS productos_activos,
    COUNT(*)                        AS total_ordenes,
    SUM(Ingreso_Total)              AS ingreso_total,
    SUM(Ganancia_Bruta)             AS ganancia_bruta,
    ROUND(
        SUM(Ganancia_Bruta) * 100.0
        / NULLIF(SUM(Ingreso_Total), 0), 2
    )                               AS margen_pct
FROM dbo.ordenes
GROUP BY Categoria
ORDER BY ingreso_total DESC;
