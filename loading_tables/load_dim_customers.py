from src.loaders import append_via_sqlalchemy
import pandas as pd
from src.utils import log

def load_customers():
    df = pd.read_csv('data/cleaned/customers.csv')
    log.info(f'Loading {len(df)} rows')
    
    
    df['first_order_date'] = pd.to_datetime(df['first_order_date']).dt.date
    df['last_order_date'] = pd.to_datetime(df['last_order_date']).dt.date
    df = df.drop_duplicates(subset=['customer_unique_id'])
        
    print(type(df.loc[0,'last_order_date'])) # casting done perfectly
    
    # loading the table 
    append_via_sqlalchemy(
        df=df,
        table_name='dim_customers',
        schema='warehouse'
    )
    
    
load_customers()
    
    
    

