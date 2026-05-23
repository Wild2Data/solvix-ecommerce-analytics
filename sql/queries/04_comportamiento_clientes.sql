-- ============================================================
-- 04 — Comportamiento de clientes
-- Frecuencia, ticket promedio y ciudades top
-- Base para segmentación RFM (Python notebook 04)
-- ============================================================

USE solvix_analytics;

-- ── Métricas por cliente ────────────────────────────────────
SELECT
    ID_Cliente,
    COUNT(*)                            AS total_ordenes,
    SUM(Cantidad)                       AS unidades_compradas,
    SUM(Ingreso_Total)                  AS ingreso_total,
    ROUND(AVG(CAST(Ingreso_Total AS FLOAT)), 2)
                                        AS ticket_promedio,
    MIN(Fecha)                          AS primera_compra,
    MAX(Fecha)                          AS ultima_compra,
    DATEDIFF(day, MIN(Fecha), MAX(Fecha))
                                        AS dias_como_cliente,
    -- Días desde última compra (base para recencia en RFM)
    DATEDIFF(day, MAX(Fecha), '2026-04-30')
                                        AS dias_sin_comprar
FROM dbo.ordenes
GROUP BY ID_Cliente
ORDER BY ingreso_total DESC;


-- ── Distribución por ciudad ─────────────────────────────────
SELECT
    Ciudad_Destino,
    COUNT(*)                            AS total_ordenes,
    COUNT(DISTINCT ID_Cliente)          AS clientes_unicos,
    SUM(Ingreso_Total)                  AS ingreso_total,
    ROUND(
        SUM(Ingreso_Total) * 100.0
        / SUM(SUM(Ingreso_Total)) OVER (), 2
    )                                   AS pct_ingreso_total,
    SUM(CASE WHEN Estado_Envio = 'Devuelto'
             THEN 1 ELSE 0 END)         AS devoluciones,
    ROUND(
        SUM(CASE WHEN Estado_Envio = 'Devuelto'
                 THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 2
    )                                   AS tasa_devolucion_pct
FROM dbo.ordenes
GROUP BY Ciudad_Destino
ORDER BY ingreso_total DESC;


-- ── Patrones temporales: ventas por día de semana ───────────
SELECT
    Dia_Semana,
    COUNT(*)                            AS total_ordenes,
    SUM(Ingreso_Total)                  AS ingreso_total,
    ROUND(AVG(CAST(Ingreso_Total AS FLOAT)), 2)
                                        AS ticket_promedio
FROM dbo.ordenes
GROUP BY Dia_Semana
ORDER BY total_ordenes DESC;
