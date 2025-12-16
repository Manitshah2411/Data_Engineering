import pandas as pd
from src.loaders import append_via_sqlalchemy
from src.utils import log

def load_dim_products():
    df = pd.read_csv('data/cleaned/products.csv')
    log.info(f'Loading {len(df)} rows')
    
    # As validation of this is done separately directly insertion is the next step
    
    append_via_sqlalchemy(
        df=df,
        table_name='dim_products',
        schema='warehouse'
    )
    
    
    log.info(f'Loading Done!!!')
    
load_dim_products()