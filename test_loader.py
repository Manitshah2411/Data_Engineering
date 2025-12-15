from src.loaders import append_via_sqlalchemy
from src.db_engine import get_engine
import pandas as pd
from sqlalchemy import text

def test_loader():
    df = pd.DataFrame(
        [
            {
                "cust_unique_id": "test1245",
                "cust_id": "cid001",
                "cust_city": "Mumbai",
                "cust_state": "MH",
                "first_order_date": "2024-01-01",
                "last_order_date": "2024-05-01",
                "num_orders": 2,
                "total_revenue": 400.00,
                "active": True
            }
        ]
    )
    
    df['first_order_date'] = pd.to_datetime(df['first_order_date']).dt.date
    df['last_order_date'] = pd.to_datetime(df['last_order_date']).dt.date
    append_via_sqlalchemy(df,'dim_customers')
    
def checking_data():
    engine = get_engine(echo=False)
    
    with engine.connect() as conn:
        results = conn.execute(text("""
        SELECT * 
        FROM warehouse.dim_customers
        LIMIT 10;
        """))
        
        print(results.fetchall())
        
if __name__ == '__main__':
    checking_data()
    
    
    