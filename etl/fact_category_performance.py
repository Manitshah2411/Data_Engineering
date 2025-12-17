from src.db_engine import get_engine
from sqlalchemy import text
from src.utils import log

def fact_category_performance():
    engine = get_engine()
    
    sql = f"""
    TRUNCATE TABLE warehouse.fact_category_performance;
    
    INSERT INTO warehouse.fact_category_performance
    SELECT 
        p.product_category_name,
        SUM(oi.price) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS total_units_sold, -- Also same as num_orders as here the quantity is always 1
        COUNT(DISTINCT p.product_id) AS num_products,
        ROUND(AVG(oi.price),2) AS avg_price
    FROM warehouse.fact_order_items AS oi
    JOIN warehouse.dim_orders AS o
    ON o.order_id = oi.order_id
    JOIN warehouse.dim_products AS p
    ON p.product_id = oi.product_id
    GROUP BY p.product_category_name;
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
    
    log.info('Executed!!!')    
    
if __name__ == "__main__":
    fact_category_performance()
    