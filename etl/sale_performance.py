from sqlalchemy import text
from src.db_engine import get_engine
from src.utils import log
from src.metadata import(
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run
)

PIPELINE_NAME = "sale_performance"

config = get_pipeline_config(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME)
engine = get_engine()

try:
    with engine.begin() as conn:
        if config['truncate_before_load']:
            log.info(f"Truncation {PIPELINE_NAME} table")
            conn.execute(text(f"""
                         TRUNCATE TABLE {config['target_schema']}.{config['target_table']}
                         """))
            
            log.info("Running SQL Aggregations...")
            
            result = conn.execute(text(f"""
                        INSERT INTO {config['target_schema']}.{config['target_table']}(
                            seller_id,
                            total_orders,
                            total_revenue,
                            avg_order_value,
                            total_items_sold,
                            first_sales_date,
                            last_sales_date
                        )
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
                                       """))
            rows_processed = result.rowcount
            
        end_pipeline_run(
            run_id=run_id,
            status='SUCCESS',
            rows_processed=rows_processed
        )
        
except Exception as e:
    log.info("Pipeline Failed!!!")
    
    end_pipeline_run(
        run_id=run_id,
        status='FAILED',
        error_message=str(e)
    )
    
    raise
