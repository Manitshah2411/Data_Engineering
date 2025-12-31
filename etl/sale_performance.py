from sqlalchemy import text
from src.db_engine import get_engine
from src.utils import log
from src.metadata import(
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run,
    get_last_successful_watermark
)

PIPELINE_NAME = "sale_performance"

config = get_pipeline_config(PIPELINE_NAME)
last_watermark = get_last_successful_watermark(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME,watermark_used=last_watermark)
engine = get_engine()

try:
    with engine.begin() as conn:    
        log.info("Running SQL Aggregations...")
        
        upsert = text(f"""
                    WITH incremental AS (
                        SELECT 
                        oi.seller_id,
                        COUNT(DISTINCT o.order_id) AS total_orders,
                        SUM(oi.price) AS total_revenue,
                        ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id),2) AS avg_order_value,
                        COUNT(*) AS total_items_sold,
                        MIN(o.order_purchase_timestamp) AS first_sales_date,
                        MAX(o.order_purchase_timestamp) AS last_sales_date
                    FROM warehouse.fact_order_items AS oi
                    JOIN warehouse.dim_products AS p
                    ON p.product_id = oi.product_id
                    JOIN warehouse.dim_orders AS o
                    ON o.order_id = oi.order_id
                    WHERE (:last_watermark) IS NULL
                    OR o.order_purchase_timestamp > :last_watermark
                    GROUP BY oi.seller_id
                    )
                    INSERT INTO {config['target_schema']}.{config['target_table']} AS sp(
                        seller_id,
                        total_orders,
                        total_revenue,
                        avg_order_value,
                        total_items_sold,
                        first_sales_date,
                        last_sales_date
                    )
                    SELECT 
                        seller_id,
                        total_orders,
                        total_revenue,
                        avg_order_value,
                        total_items_sold,
                        first_sales_date,
                        last_sales_date
                    FROM incremental 
                    ON CONFLICT(seller_id)
                    DO UPDATE SET 
                    total_orders = sp.total_orders + EXCLUDED.total_orders,
                    total_revenue = sp.total_revenue + EXCLUDED.total_revenue,
                    avg_order_value = (sp.total_revenue + EXCLUDED.total_revenue) /
                                (sp.total_orders + EXCLUDED.total_orders),
                    total_items_sold = sp.total_items_sold + EXCLUDED.total_items_sold,
                    first_sales_date = LEAST(sp.first_sales_date, EXCLUDED.first_sales_date),
                    last_sales_date = GREATEST(sp.last_sales_date, EXCLUDED.last_sales_date)
                                    """)
        result = conn.execute(upsert,{"last_watermark":last_watermark})
        rows_processed = result.rowcount
        
        watermark = text("""
                    SELECT MAX(o.order_purchase_timestamp)
                    FROM warehouse.fact_order_items AS fo
                    JOIN warehouse.dim_orders AS o
                    ON o.order_id = fo.order_id
                    WHERE (:last_watermark) IS NULL
                    OR o.order_purchase_timestamp > :last_watermark
                        """)
        
        new_watermark = conn.execute(watermark,{"last_watermark":last_watermark}).scalar()
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
