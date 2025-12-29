from src.db_engine import get_engine
from sqlalchemy import text
from datetime import datetime
from src.utils import log

engine = get_engine()

##################################################################

def get_pipeline_config(pipeline_name: str) -> dict:
    """
    Fetches the table_name, schema_name, target_table of the pipeline. 
    Which is used in future configs
    """
    
    sql = text("""
               SELECT  
                    pipeline_name,
                    target_schema,
                    target_table,
                    load_type,
                    watermark_column,
                    truncate_before_load,
                    allow_updates,
                    is_active
                FROM meta.config
                WHERE pipeline_name = :pipeline_name
               """)
    
    with engine.connect() as conn:
        result = conn.execute(sql,{"pipeline_name" : pipeline_name}).mappings().fetchone()
        # mappings : sqlalchemy give results in tuple, so mappings() converts each row into dictionary
        # fetchone() : it gives one row or None
    
    if not result:
        raise ValueError(f"No config found for pipline : {pipeline_name}")
    # If the result is empty than Valueerror is raised
    
    if not result['is_active']:
        raise RuntimeError(f"Pipeline {pipeline_name} is marked inactive")
    # If the pipeline is marked inactive than too runtimeerror is raised
    
    
    return dict(result)
        
##################################################################
  
def start_pipeline(pipeline_name: str, watermark_used=None) -> int:
    """
    Registers a new pipeline.
    It executes only IN_PROGESS run per pipeline.
    """
    
    sql = text("""
               INSERT INTO meta.etl_runs(
                   pipeline_name,
                   status,
                   start_time,
                   watermark_used
               )
               VALUES(
                   :pipeline_name,
                   'IN_PROGRESS',
                   NOW(),
                   :watermark_used
               )
               
               RETURNING run_id
               """)
    
    # returning run_id is auto-generated in postgres which is returned and will be used in python
    
    with engine.begin() as conn:
        run_id = conn.execute(sql,{
            "pipeline_name" : pipeline_name,
            "watermark_used" : watermark_used
        }).scalar() # it gives a single value as a result
        
    
    log.info(f'Started pipeline run : {run_id} for {pipeline_name}')
    
    return run_id

##################################################################

def get_last_successful_watermark(pipeline_name: str):
    """
    Gets the last successful watermark of the pipeline
    Returns None if the pipeline never ran successfully
    """
    
    sql = text("""
               SELECT MAX(watermark_used)
               FROM meta.etl_runs
               WHERE pipline_name = :pipeline_name
                AND status = 'SUCCESS'
               """)
    
    with engine.connect() as conn:
        watermark = conn.execute(sql, {"pipline_name": pipeline_name}).scalar
        
    return watermark


def end_pipeline_run(run_id: int, status: str, rows_processed: int=None, error_message: str=None):
    """
    Marks the pipeline as SUCCESS or FAIL after a run.
    """
    
    if status not in("SUCCESS","FAILED"):
        raise ValueError("Status must be SUCCESS or FAIL")
    
    sql = text("""
               UPDATE meta.etl_runs
               SET 
                    status = :status,
                    end_time = NOW(),
                    rows_processed = :rows_processed,
                    error_message = :error_message
                WHERE run_id = :run_id
               """)
    
    with engine.begin() as conn:
        conn.execute(sql, {
            "run_id" : run_id,
            "status" : status,
            "rows_processed" : rows_processed,
            "error_message" :error_message
        })
        
    log.info(f"Pipeline with run {run_id} ended with status {status}")