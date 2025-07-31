import psycopg2
from db.db_config import get_engine

engine = get_engine()

# List of tables to delete
tables_to_drop = ["doaj", "openapc", "pubmed", "enriched_pubmed_data"]

# Create comma-separated string of table names
table_names_str = ", ".join([f"{table}" for table in tables_to_drop])

# SQL to drop all tables
drop_sql = f"DROP TABLE IF EXISTS {table_names_str};"

try:
    # Get raw DB connection from SQLAlchemy engine
    conn = engine.raw_connection()
    cursor = conn.cursor()

    # Execute drop command
    cursor.execute(drop_sql)
    conn.commit()

    print(f"Tables {tables_to_drop} have been deleted (if they existed).")

except psycopg2.Error as e:
    print("An error occurred:", e)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
