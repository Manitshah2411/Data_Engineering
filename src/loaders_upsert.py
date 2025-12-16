from sqlalchemy import text
from src.db_engine import get_engine
import pandas as pd
from src.utils import log

# This function is used when the data is needed to be updated while inserting when the new data comes in
# The append_via_sqlalchemy is one time use bulk insert function that is very fast for new tables
def upsert_customers(df: pd.DataFrame, table_name: str, schema: str):
    
    df['first_order_date'] = pd.to_datetime(df['first_order_date']).dt.date
    df['last_order_date'] = pd.to_datetime(df['last_order_date']).dt.date
    
    rows = df.to_dict(orient='records') # This is the actual data which will be passed that is converted into list of dict
    # each row conists of a single person data or a thing
    
    sql = f"""
    INSERT INTO {schema}.{table_name} (
        customer_id,
        customer_unique_id,
        customer_city,
        customer_state,
        first_order_date,
        last_order_date,
        num_orders,
        total_revenue,
        active
    )
    VALUES (
        :customer_id,
        :customer_unique_id,
        :customer_city,
        :customer_state,
        :first_order_date,
        :last_order_date,
        :num_orders,
        :total_revenue,
        :active
    )
    ON CONFLICT (customer_unique_id) DO UPDATE SET
        customer_id = EXCLUDED.customer_id,
        customer_city = EXCLUDED.customer_city,
        customer_state = EXCLUDED.customer_state,
        first_order_date = EXCLUDED.first_order_date,
        last_order_date = EXCLUDED.last_order_date,
        num_orders = EXCLUDED.num_orders,
        total_revenue = EXCLUDED.total_revenue,
        active = EXCLUDED.active;
    """
    # If the primary key(customer_unique_id) is repeated than the old data is replaced with the EXCLUDED(old) data
    
    engine = get_engine(echo=False)
    
    with engine.connect() as conn:
        conn.execute(text(sql),rows)
        
    log.info(f'Upsert Completed of {len(rows)} rows')
    