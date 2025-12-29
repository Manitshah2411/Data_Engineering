from sqlalchemy import text
from src.db_engine import get_engine
from src.utils import log
from src.metadata import(
    get_pipeline_config,
    start_pipeline,
    end_pipeline_run
)

PIPELINE_NAME = "fact_customer_lifecycle"

config = get_pipeline_config(PIPELINE_NAME)
run_id = start_pipeline(PIPELINE_NAME)
engine = get_engine()

print(config,run_id)

try:
    with engine.begin() as conn:
        if config['truncate_before_load']:
            log.info(f"Truncation {PIPELINE_NAME} table")
            conn.execute(text(f"""
                         TRUNCATE TABLE {config['target_schema']}.{config['target_table']}
                         """))
            
            log.info("Running SQL Aggregations...")
            
            result = conn.execute(text(f"""
                            INSERT INTO {config['target_schema']}.{config['target_table']} (
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
                            GROUP BY  o.customer_unique_id;
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


    
        
