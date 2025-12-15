from src.db_engine import get_engine
import pandas as pd
from src.utils import log

def append_via_sqlalchemy(
    df: pd.DataFrame,
    table_name: str,
    schema: str = 'warehouse',
    chunksize: int = 5000
    ):
    
    """
    This method is used to append(or other replace or fail) to the postgres tables
    Uses pandas.to_sql internally to append it

    Params:
        df -> The dataframe which is to be loaded
        table_name -> The table name in the postgres in which the data is need to be appended
        schema -> The schema in which the table is
        chunksize -> Chunk of data which is loaded at once(For efficiency and avoid crashing)
    """
    
    engine = get_engine()
    
    log.info(f"Loading {len(df)} rows into {schema}.{table_name}...")
    
    # The transaction block, This where the actual connection begins
    with engine.begin() as conn:
        df.to_sql(
            name=table_name, # Name of the table in which it is needed to be appended
            schema=schema, # Schema in which the table is
            con=conn,
            if_exists='append', # Mode : here append means append to the current data, don't overwrite it
            index=False, # Don't have default index like 0,1,2,3,4...
            method='multi', # method multi means load multiple data at once
            chunksize=chunksize # chunksize decided at once how rows should we load it
        )
    
