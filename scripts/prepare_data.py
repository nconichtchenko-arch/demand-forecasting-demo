import pandas as pd
from sqlalchemy import create_engine
import os

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "dwh_marketplace",
    "user": "dwh_user",
    "password": "dwh_password",
}

def get_daily_revenue():
    engine = create_engine(
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )
    query = """
        SELECT order_date, SUM(total_revenue) AS revenue
        FROM dbt_schema.fct_sales
        GROUP BY order_date
        ORDER BY order_date
    """
    df = pd.read_sql(query, engine)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

if __name__ == "__main__":
    df = get_daily_revenue()
    print(df.head())
    print(f"Всего дней: {len(df)}")
    df.to_csv('data/daily_revenue.csv', index=False)
