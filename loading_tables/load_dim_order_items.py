import pandas as pd
from src.loaders import append_via_sqlalchemy
from src.utils import log

def load_dim_orders_items():
    df = pd.read_csv('data/cleaned/order_items.csv')
    log.info(f'Loading {len(df)} rows')
    
    append_via_sqlalchemy(
        df=df,
        table_name='fact_order_items',
        schema='warehouse'
    )
    
    log.info('Loading Done!!')

load_dim_orders_items()