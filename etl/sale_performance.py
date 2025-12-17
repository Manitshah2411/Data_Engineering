from src.db_engine import get_engine
from sqlalchemy import text
from src.utils import log

def sale_performance():
    engine = get_engine()
    
    sql = f"""
    TRUNCATE TABLE warehouse.sale_performance;
    
    INSERT INTO warehouse.sale_performance
    SELECT 
        oi.seller_id,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.price) AS total_revenue,
        ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id),2) AS avg_order_value,
        COUNT(DISTINCT p.product_id) AS total_items_sold,
        MIN(o.order_purchase_timestamp) AS first_sales_date,
        MAX(o.order_purchase_timestamp) AS last_sales_date
    FROM warehouse.fact_order_items AS oi
    JOIN warehouse.dim_products AS p
    ON p.product_id = oi.product_id
    JOIN warehouse.dim_orders AS o
    ON o.order_id = oi.order_id
    GROUP BY oi.seller_id
    ORDER BY COUNT(DISTINCT o.order_id) DESC;
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        
    log.info('Executed Successfully!!!')
    
if __name__ == "__main__":
    sale_performance()