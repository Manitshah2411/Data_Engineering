import pandas as pd

REQUIRED_COLUMNS = {
    "customer_id",
    "customer_unique_id",
    "customer_city",
    "customer_state",
    "first_order_date",
    "last_order_date",
    "num_orders",
    "total_revenue",
    "active",
    
}

PRIMARY_KEY = 'customer_unique_id'

def validate_customers(df: pd.DataFrame):
    # Columns existence
    missing = REQUIRED_COLUMNS - set(df.columns)
    extra = set(df.columns) - REQUIRED_COLUMNS
    
    if missing:
        raise ValueError(f'Column missing : {missing}')
    
    if extra:
        raise ValueError(f'Extra Columns : {extra}')
    
    
    # Primary Key integrity checks
    if df[PRIMARY_KEY].isna().any():
        raise ValueError('Primary key contains nulls')
    
    if df[PRIMARY_KEY].duplicated().any():
        raise ValueError('Duplicate Primary key')
    
    # general logic checks
    if (df['num_orders'] < 0).any():
        raise ValueError('Negative Num of orders')
    
    if (df['total_revenue'] < 0).any():
        raise ValueError('Negative Revenue')
    
    print('Validation Done!!!')