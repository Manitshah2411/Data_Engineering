from sqlalchemy import text
from src.db_engine import get_engine
from src.metadata import(
    start_pipeline,
    end_pipeline_run,
    get_pipeline_config
)
from src.utils import log

PIPELINE_NAME = "fact_daily_sales"
engine = get_engine()

config = get_pipeline_config(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME)

try:
    with engine.begin() as conn:
        if config['truncate_before_load']:
            log.info(f'Truncating {PIPELINE_NAME} table.')
            conn.execute(text(f"""
                        TRUNCATE TABLE {config['target_schema']}.{config['target_table']}
                         """))
            
            log.info('Running SQL Aggregations...')
        
            result = conn.execute(text(f"""
                    INSERT INTO {config['target_schema']}.{config['target_table']} (
                        sales_date,
                        total_revenue,
                        total_order,
                        total_items,
                        total_customers,
                        avg_order_value
                    )
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
                                    """))
            rows_processed = result.rowcount
            
        end_pipeline_run(run_id=run_id,
                         status='SUCCESS',
                         rows_processed=rows_processed)
        
        

    
except Exception as e:
    log.info('Pipeline Failed!!!')
    
    end_pipeline_run(run_id=run_id,
                     status='FAILED',
                     error_message=str(e)
                     )
    
    raise
    
    