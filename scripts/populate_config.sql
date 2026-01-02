INSERT INTO meta.config(pipeline_name,target_schema,target_table,load_type,truncate_before_load,allow_updates,is_active)
VALUES('fact_daily_sales','warehouse','fact_daily_sales','FULL',TRUE,FALSE,TRUE);

INSERT INTO meta.config(pipeline_name,target_schema,target_table,load_type,truncate_before_load,allow_updates,is_active)
VALUES('fact_category_performance','warehouse','fact_category_performance','FULL',TRUE,FALSE,TRUE);

INSERT INTO meta.config(pipeline_name,target_schema,target_table,load_type,truncate_before_load,allow_updates,is_active)
VALUES('fact_customer_lifecycle','warehouse','fact_customer_lifecycle','FULL',TRUE,FALSE,TRUE);

INSERT INTO meta.config(pipeline_name,target_schema,target_table,load_type,truncate_before_load,allow_updates,is_active)
VALUES('fact_product_performance','warehouse','fact_product_performance','FULL',TRUE,FALSE,TRUE);

INSERT INTO meta.config(pipeline_name,target_schema,target_table,load_type,truncate_before_load,allow_updates,is_active)
VALUES('sale_performance','warehouse','sale_performance','FULL',TRUE,FALSE,TRUE);

INSERT INTO meta.config(pipeline_name,target_schema,target_table,load_type,truncate_before_load,allow_updates,is_active)
VALUES('customers_upsert','warehouse','dim_customers','FULL',TRUE,FALSE,TRUE)

