import pandas as pd
from utils.utils import normalize
from db.db_config import get_engine
from sqlalchemy import text

# db to load for final dash and initialise db engine
TABLE_NAME = "enriched_pubmed_data"
engine = get_engine()

def load_data_from_db():
    query = f"SELECT * FROM {TABLE_NAME} ORDER BY pmid;"
    df = pd.read_sql(query, engine)

    df["doi"] = normalize(df["doi"])
    df["issn"] = normalize(df["issn"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["country"] = df["country"].fillna("Unknown")
    df["journal"] = df["journal"].fillna("Unknown")
    df["match_source"] = df["match_source"].fillna("Unmatched")
    df["total_price_eur"] = pd.to_numeric(df["total_price_eur"], errors="coerce")
    df["cost_price_eur"] = pd.to_numeric(df["cost_price_eur"], errors="coerce")
    df["estimated_price_eur"] = pd.to_numeric(df["estimated_price_eur"], errors="coerce")
    return df

def get_table_name():
    return TABLE_NAME

def get_engine():
    return engine

def save_to_postgres(
    df,
    engine,
    table_name,
    logger=None,
    create_sql=None,
    if_exists="append",           # "replace" or "append"
    clear_existing=False,         # run DELETE FROM table
    chunk_size=None               # use chunked insert or not
):
    if df.empty:
        msg = f"No data to save to PostgreSQL table '{table_name}'."
        logger.warning(msg) if logger else print(msg)
        return

    with engine.begin() as conn:
        if create_sql:
            conn.execute(text(create_sql))
        if clear_existing:
            conn.execute(text(f"DELETE FROM {table_name};"))

    insert_msg = f"Inserting {len(df)} rows into '{table_name}'..."
    logger.info(insert_msg) if logger else print(f"⬆️ {insert_msg}")

    if chunk_size:
        from tqdm import tqdm
        for start in tqdm(range(0, len(df), chunk_size), desc=f"📥 {table_name}"):
            chunk = df.iloc[start:start + chunk_size]
            chunk.to_sql(table_name, con=engine, if_exists=if_exists, index=False)
    else:
        df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)

    done_msg = f"Saved {len(df)} rows to '{table_name}'"
    logger.info(done_msg) if logger else print(done_msg)



