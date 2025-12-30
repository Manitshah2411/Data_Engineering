from sqlalchemy import text
from src.db_engine import get_engine
from src.metadata import(
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run,
    get_last_successful_watermark
)
from src.utils import log

PIPELINE_NAME = "fact_category_performance"

engine = get_engine()
config = get_pipeline_config(PIPELINE_NAME)
last_watermak = get_last_successful_watermark(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME, watermark_used=last_watermak)

try:
    with engine.begin() as conn:
        log.info("Running SQL Aggregations...")
        upsert = text(f"""
                    WITH incremental AS(
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
                        WHERE (:last_watermark) IS NULL
                        OR o.order_purchase_timestamp > :last_watermark
                        GROUP BY p.product_category_name
                    )
                    INSERT INTO {config['target_schema']}.{config['target_table']} AS fcp (
                        product_category_name,
                        total_revenue,
                        total_units_sold,
                        num_products,
                        avg_price
                        )
                    SELECT 
                        product_category_name,
                        total_revenue,
                        total_units_sold,
                        num_products,
                        avg_price
                    FROM incremental
                    ON CONFLICT (product_category_name)
                    DO UPDATE SET
                            total_revenue = fcp.total_revenue + EXCLUDED.total_revenue,
                            total_units_sold = fcp.total_revenue + EXCLUDED.total_units_sold,
                            num_products = fcp.num_products + EXCLUDED.num_products,
                            avg_price = fcp.avg_price + EXCLUDED.avg_price;
                        """)
        
        result = conn.execute(upsert,{"last_watermark":last_watermak})
        rows_processed = result.rowcount
        
        watermark_sql = text("""
                        SELECT MAX(o.order_purchase_timestamp) 
                        FROM warehouse.fact_order_items AS fo
                        JOIN warehouse.dim_orders AS o
                        ON o.order_id = fo.order_id
                        WHERE (:last_watermark) IS NULL
                        OR o.order_purchase_timestamp > :last_watermark
                            """)
        
        new_watermark = conn.execute(watermark_sql,{"last_watermark":last_watermak}).scalar()
        final_watermark = new_watermark or last_watermak
        
        end_pipeline_run(
            run_id=run_id,
            status='SUCCESS',
            rows_processed=rows_processed,
            watermark_used=final_watermark
        )
        
except Exception as e:
    log.info('Pipeline failed!!!')
    
    end_pipeline_run(
        run_id=run_id,
        status='FAILED',
        error_message=str(e)
    )
    
    raise

