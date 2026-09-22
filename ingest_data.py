import os
import pandas as pd
from sqlalchemy import create_engine

# Database Connection URI
DATABASE_URI = "postgresql://olist_user:olist_password@localhost:5432/olist_db"
engine = create_engine(DATABASE_URI)

# Ordered mapping: Table name -> CSV file name (Respecting FK dependencies)
FILES_TO_TABLES = [
    ("product_category_name_translation", "product_category_name_translation.csv"),
    ("customers", "olist_customers_dataset.csv"),
    ("sellers", "olist_sellers_dataset.csv"),
    ("products", "olist_products_dataset.csv"),
    ("geolocation", "olist_geolocation_dataset.csv"),
    ("orders", "olist_orders_dataset.csv"),
    ("order_items", "olist_order_items_dataset.csv"),
    ("order_payments", "olist_order_payments_dataset.csv"),
    ("order_reviews", "olist_order_reviews_dataset.csv"),
]

def ingest_data():
    for table_name, file_name in FILES_TO_TABLES:
        if not os.path.exists(file_name):
            print(f"Warning: File {file_name} not found. Skipping...")
            continue

        print(f"Loading {file_name} into table '{table_name}'...")
        df = pd.read_csv(file_name)

        # Handling potential duplicate primary keys in geolocation
        if table_name == "geolocation":
            df = df.drop_duplicates()

        # Insert data in chunks for performance and memory efficiency
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",
            index=False,
            chunksize=10000,
            method="multi"
        )
        print(f"Successfully ingested {len(df)} rows into '{table_name}'.")

if __name__ == "__main__":
    ingest_data()