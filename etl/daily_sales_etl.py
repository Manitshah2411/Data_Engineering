from sqlalchemy import text
from src.db_engine import get_engine
from src.metadata import(
    start_pipeline,
    end_pipeline_run,
    get_pipeline_config,
    get_last_successful_watermark
)
from src.utils import log

PIPELINE_NAME = "fact_daily_sales"
engine = get_engine()

config = get_pipeline_config(PIPELINE_NAME)
last_watermark = get_last_successful_watermark(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME,watermark_used=last_watermark)


try:
    first_run = last_watermark is None
    with engine.begin() as conn:
        log.info("Deleting affected sales date...")
        
        delete = text(f"""
                    DELETE FROM {config['target_schema']}.{config['target_table']}
                    WHERE sales_date IN(
                        SELECT DISTINCT DATE_TRUNC('day',o.order_purchase_timestamp)
                    FROM warehouse.fact_order_items AS fo
                    JOIN warehouse.dim_orders AS o
                    ON o.order_id = fo.order_id
                    WHERE :last_watermark IS NULL
                    OR o.order_purchase_timestamp > :last_watermark
                    )
                          """)
        conn.execute(delete,{"last_watermark" : last_watermark})
        
        
        log.info('Running SQL Aggregations...')
    
        insert = text(f"""
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
                WHERE :last_watermark IS NULL
                OR DATE_TRUNC('day', o.order_purchase_timestamp) >= DATE_TRUNC('day', last_watermark)
                GROUP BY DATE_TRUNC('day',o.order_purchase_timestamp)
                ORDER BY SUM(price) DESC;
                                """)
        result = conn.execute(insert,{"last_watermark" : last_watermark})
        
        watermark = text("""
                    SELECT MAX(o.order_purchase_timestamp)
                    FROM warehouse.fact_order_items fo
                    JOIN warehouse.dim_orders o
                    ON fo.order_id = o.order_id
                    WHERE (:last_watermark IS NULL)
                    OR o.order_purchase_timestamp > :last_watermark; 
                        """)
        
        new_watermark = conn.execute(watermark,{"last_watermark":last_watermark}).scalar()
        
        final_watermark = new_watermark or last_watermark
        
        rows_processed = result.rowcount
            
        end_pipeline_run(run_id=run_id,
                         status='SUCCESS',
                         rows_processed=rows_processed,
                         watermark_used=final_watermark)
        
except Exception as e:
    log.info('Pipeline Failed!!!')
    
    end_pipeline_run(run_id=run_id,
                     status='FAILED',
                     error_message=str(e)
                     )
    
    raise
    
    