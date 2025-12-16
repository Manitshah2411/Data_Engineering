from sqlalchemy import text
from src.db_engine import get_engine

def daily_sales_etl():
    sql = f"""
    TRUNCATE TABLE warehouse.fact_daily_sales;
    
    INSERT INTO warehouse.fact_daily_sales
    SELECT 
        DATE_TRUNC('day',o.order_purchase_timestamp) AS sales_date,
        SUM(fo.price) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS total_order,
        COUNT(p.product_id) AS total_items,
        COUNT(DISTINCT c.customer_id) AS total_customers,
        ROUND(SUM(fo.price) / COUNT(DISTINCT o.order_id),2) AS avg_order_value
    FROM warehouse.fact_order_items AS fo
    JOIN warehouse.dim_orders AS o
        ON fo.order_id = o.order_id
    JOIN warehouse.dim_products AS p
        ON p.product_id = fo.product_id
    JOIN warehouse.dim_customers AS c
        ON c.customer_unique_id = o.customer_unique_id
    GROUP BY DATE_TRUNC('day',o.order_purchase_timestamp)
    ORDER BY SUM(price) DESC;
    """
    
    engine = get_engine()
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        
    print('ETL completed!!!')
    
if __name__ == "__main__":
    daily_sales_etl()