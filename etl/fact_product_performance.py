from sqlalchemy import text
from src.db_engine import get_engine
from src.utils import log
from src.metadata import(
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run
)

PIPELINE_NAME = "fact_product_performance"

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
                             product_id,
                            product_category_name,
                            total_units_sold,
                            total_revenue,
                            avg_selling_price,
                            first_sold_date,
                            last_sold_date
                        )
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
                        GROUP BY p.product_id,
                            p.product_category_name
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
