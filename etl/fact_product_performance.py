from src.db_engine import get_engine
from sqlalchemy import text
from src.utils import log

def fact_product_performance():
    engine = get_engine()
    
    sql = f"""
    TRUNCATE TABLE warehouse.fact_product_performance;
    
    INSERT INTO warehouse.fact_product_performance
        SELECT 
        p.product_id,
        p.product_category_name,
        COUNT(DISTINCT o.order_id) AS total_units_sold,
        SUM(oi.price) AS total_revenue,
        SUM(oi.price) / COUNT(DISTINCT o.order_id) AS avg_selling_price,
        MIN(o.order_purchase_timestamp) AS first_sold_date,
        MAX(o.order_purchase_timestamp) AS last_sold_date
    FROM warehouse.fact_order_items AS oi
    JOIN warehouse.dim_products AS p
        ON p.product_id = oi.product_id
    JOIN warehouse.dim_orders AS o
        ON o.order_id = oi.order_id
    GROUP BY p.product_id, p.product_category_name
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        
    log.info('Execution completed!!!!')
    

if __name__ == "__main__":
    fact_product_performance()
    
    
    
    