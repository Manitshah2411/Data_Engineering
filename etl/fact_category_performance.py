from sqlalchemy import text
from src.db_engine import get_engine
from src.metadata import(
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run
)
from src.utils import log

PIPELINE_NAME = "fact_category_performance"

engine = get_engine()
config = get_pipeline_config(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME)

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
                            product_category_name,
                            total_revenue,
                            total_units_sold,
                            num_products,
                            avg_price
                         )
                        SELECT 
                            p.product_category_name,
                            SUM(oi.price) AS total_revenue,
                            COUNT(DISTINCT o.order_id) AS total_units_sold,
                            COUNT(DISTINCT p.product_id) AS num_products,
                            ROUND(AVG(oi.price),2) AS avg_price
                        FROM warehouse.fact_order_items AS oi
                        JOIN warehouse.dim_orders AS o
                        ON o.order_id = oi.order_id
                        JOIN warehouse.dim_products AS p
                        ON p.product_id = oi.product_id
                        GROUP BY p.product_category_name;
                         """))
            rows_processed = result.rowcount
            
        end_pipeline_run(
            run_id=run_id,
            status='SUCCESS',
            rows_processed=rows_processed
        )
        
except Exception as e:
    log.info('Pipeline failed!!!')
    
    end_pipeline_run(
        run_id=run_id,
        status='FAILED',
        error_message=str(e)
    )
    
    raise

