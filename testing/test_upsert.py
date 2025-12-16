import pandas as pd
from  validators.val_customers import validate_customers
from src.loaders_upsert import upsert_customers

df = pd.DataFrame([
    {
        "customer_id": "XYZ123",
        "customer_unique_id": "abc999",
        "customer_city": "mumbai",
        "customer_state": "MH",
        "first_order_date": "2024-01-01",
        "last_order_date": "2024-05-01",
        "num_orders": 5,
        "total_revenue": 770.0,
        "active": True
    }
])

df["first_order_date"] = pd.to_datetime(df["first_order_date"])
df["last_order_date"] = pd.to_datetime(df["last_order_date"])

validate_customers(df)
upsert_customers(df,'dim_customers','warehouse')
