from sqlalchemy import text
from src.db_engine import get_engine
from src.utils import log
from src.metadata import(
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run,
    get_last_successful_watermark
)

PIPELINE_NAME = "fact_product_performance"

config = get_pipeline_config(PIPELINE_NAME)
last_watermark = get_last_successful_watermark(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME,watermark_used=last_watermark)
engine = get_engine()

try:
    with engine.begin() as conn:
        log.info("Running Incremental UPSERT...")
        
        upsert = text(f"""
                    WITH incremental AS(
                        SELECT 
                            p.product_id,
                            p.product_category_name,
                            COUNT(DISTINCT o.order_id) AS total_units_sold,
                            SUM(oi.price) AS total_revenue,
                            ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id),2) AS avg_selling_price,
                            MIN(o.order_purchase_timestamp) AS first_sold_date,
                            MAX(o.order_purchase_timestamp) AS last_sold_date
                        FROM warehouse.fact_order_items AS oi
                        JOIN warehouse.dim_products AS p
                        ON p.product_id = oi.product_id
                        JOIN warehouse.dim_orders AS o
                        ON o.order_id = oi.order_id
                        WHERE (:last_watermark) IS NULL
                        OR o.order_purchase_timestamp > :last_watermark
                        GROUP BY p.product_id,
                            p.product_category_name
                                    )
                    INSERT INTO {config['target_schema']}.{config['target_table']} AS fpp (
                        product_id,
                        product_category_name,
                        total_units_sold,
                        total_revenue,
                        avg_selling_price,
                        first_sold_date,
                        last_sold_date
                        )
                    SELECT 
                        product_id,
                        product_category_name,
                        total_units_sold,
                        total_revenue,
                        avg_selling_price,
                        first_sold_date,
                        last_sold_date
                    FROM incremental
                    ON CONFLICT (product_id)
                    DO UPDATE SET 
                        total_units_sold = fpp.total_units_sold + EXCLUDED.total_units_sold,
                        total_revenue = fpp.total_revenue + EXCLUDED.total_revenue,
                        avg_selling_price = (fpp.avg_selling_price + EXCLUDED.avg_selling_price) /
                                    (fpp.total_revenue + EXCLUDED.total_revenue),
                        first_sold_date = LEAST(fpp.first_sold_date,EXCLUDED.first_sold_date),
                        last_sold_date = GREATEST(fpp.last_sold_date,EXCLUDED.last_sold_date);
                                    """)
        result = conn.execute(upsert,{"last_watermark":last_watermark})
        rows_processed = result.rowcount
        
        watermark_sql = text("""
                SELECT MAX(o.order_purchase_timestamp)
                FROM warehouse.fact_order_items AS fo
                JOIN warehouse.dim_orders o
                ON o.order_id = fo.order_id
                WHERE (:last_watermark) IS NULL
                OR o.order_purchase_timestamp > :last_watermark
                        """)
        
        new_watermark = conn.execute(watermark_sql,{"last_watermark":last_watermark}).scalar()
        final_watermark = new_watermark or last_watermark
        
        end_pipeline_run(
            run_id=run_id,
            status='SUCCESS',
            rows_processed=rows_processed,
            watermark_used=final_watermark
        )
        
except Exception as e:
    log.info("Pipeline Failed!!!")
    
    end_pipeline_run(
        run_id=run_id,
        status='FAILED',
        error_message=str(e)
    )
    
    raise
