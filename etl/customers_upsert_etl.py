from src.db_engine import get_engine
from src.utils import log
from sqlalchemy import text
from src.metadata import (
    get_last_successful_watermark,
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run
)

PIPELINE_NAME = "customers_upsert"

engine = get_engine()
config = get_pipeline_config(PIPELINE_NAME)
last_watermark = get_last_successful_watermark(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME,watermark_used=last_watermark)

try:
    with engine.connect() as conn:
        log.info("SQL running...")
        upsert = text(f"""
                WITH incremental AS (
                    SELECT
                        c.customer_unique_id,
                        c.customer_id,
                        MIN(c.customer_city) AS customer_city,
                        MIN(c.customer_state) AS customer_state,
                        MIN(o.order_purchase_timestamp) AS first_order_date,
                        MAX(o.order_purchase_timestamp) AS last_order_date,
                        COUNT(DISTINCT o.order_id) AS num_orders,
                        SUM(oi.price) AS total_revenue,
                        MAX(o.order_purchase_timestamp) >= (CURRENT_DATE - INTERVAL '365 days') AS active
                    FROM warehouse.dim_customers AS c
                    JOIN warehouse.dim_orders AS o
                        ON c.customer_unique_id = o.customer_unique_id
                    JOIN warehouse.fact_order_items AS oi
                        ON oi.order_id = o.order_id
                    WHERE (:last_watermark IS NULL)
                    OR o.order_purchase_timestamp > :last_watermark
                    GROUP BY c.customer_unique_id)
                INSERT INTO {config['target_schema']}.{config['target_table']} AS dc (
                    customer_unique_id,
                    customer_id,
                    customer_city,
                    customer_state,
                    first_order_date,
                    last_order_date,
                    num_orders,
                    total_revenue,
                    active
                )
                SELECT 
                    customer_unique_id,
                    customer_id,
                    customer_city,
                    customer_state,
                    first_order_date,
                    last_order_date,
                    num_orders,
                    total_revenue,
                    active
                FROM incremental
                ON CONFLICT (customer_unique_id) 
                DO UPDATE SET
                    first_order_date = LEAST(dc.first_order_date, EXCLUDED.first_order_date),
                    last_order_date = GREATEST(dc.last_order_date, EXCLUDED.last_order_date),
                    num_orders =
                        dc.num_orders + EXCLUDED.num_orders,
                    total_revenue =
                        dc.total_revenue + EXCLUDED.total_revenue,
                    active =
                        GREATEST(dc.last_order_date, EXCLUDED.last_order_date) >= 
                        CURRENT_DATE - INTERVAL '365 days'
                
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
            run_id = run_id,
            status="SUCCESS",
            rows_processed=rows_processed,
            watermark_used=final_watermark
        )

except Exception as e:
    log.info("Pipeline Failed!!!")
    
    end_pipeline_run(
        run_id = run_id,
        status="FAILED",
        error_message=str(e)
    )
    
    raise


    
    
    
    
