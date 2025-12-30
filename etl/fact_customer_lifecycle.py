from sqlalchemy import text
from src.db_engine import get_engine
from src.utils import log
from src.metadata import(
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run,
    get_last_successful_watermark
)

PIPELINE_NAME = "fact_customer_lifecycle"

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
                            o.customer_unique_id,
                            MIN(o.order_purchase_timestamp) AS first_order_date,
                            MAX(o.order_purchase_timestamp) AS last_order_date,
                            COUNT(DISTINCT o.order_id) AS num_orders,
                            SUM(oi.price) AS total_revenue,
                            ROUND(SUM(oi.price) / COUNT(DISTINCT o.order_id),2) AS avg_order_value,
                            MAX(o.order_purchase_timestamp)::DATE - MIN(o.order_purchase_timestamp)::DATE AS days_active,
                            CASE WHEN
                                MAX(o.order_purchase_timestamp)::DATE >= (CURRENT_DATE - INTERVAL '365 days') THEN TRUE
                                ELSE FALSE
                            END AS is_active
                        FROM warehouse.dim_customers AS c
                        JOIN warehouse.dim_orders AS o
                        ON c.customer_unique_id = o.customer_unique_id
                        JOIN warehouse.fact_order_items AS oi
                        ON oi.order_id = o.order_id
                        WHERE (:last_watermark) IS NULL
                        OR o.order_purchase_timestamp > :last_watermark
                        GROUP BY  o.customer_unique_id
                      )
                        INSERT INTO {config['target_schema']}.{config['target_table']} AS fcl (
                            customer_unique_id,
                            first_order_date,
                            last_order_date,
                            num_orders,
                            total_revenue,
                            avg_order_value,
                            days_active,
                            is_active
                        )
                        SELECT 
                            customer_unique_id,
                            first_order_date,
                            last_order_date,
                            num_orders,
                            total_revenue,
                            avg_order_value,
                            days_active,
                            is_active
                        FROM incremental 
                        ON CONFLICT (customer_unique_id)
                        DO UPDATE SET
                            first_order_date = LEAST(fcl.first_order_date, EXCLUDED.first_order_date),
                            last_order_date = GREATEST(fcl.last_order_date, EXCLUDED.last_order_date),
                            num_orders = fcl.num_orders + EXCLUDED.num_orders,
                            total_revenue = fcl.total_revenue + EXCLUDED.total_revenue,
                            avg_order_value = (fcl.avg_order_value + EXCLUDED.avg_order_value) / 
                                            (fcl.num_orders + EXCLUDED.num_orders),
                            days_active = GREATEST(fcl.last_order_date, EXCLUDED.last_order_date)::DATE - 
                                        LEAST(fcl.first_order_date, EXCLUDED.first_order_date)::DATE,
                            is_active = GREATEST(fcl.last_order_date, EXCLUDED.last_order_date) >= 
                                (CURRENT_DATE - INTERVAL '365 days')
                                """)
        
        result = conn.execute(upsert,{"last_watermark":last_watermark})
        rows_processed = result.rowcount
        
        watermark_sql = text("""
                        SELECT MAX(o.order_purchase_timestamp)
                        FROM warehouse.fact_order_items AS fo
                        JOIN warehouse.dim_orders AS o
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


    
        
