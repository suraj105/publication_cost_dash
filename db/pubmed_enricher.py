import time
from tqdm import tqdm
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from db.db_config import get_engine
from db.enrichment import enrich_pubmed

# initialize db engine
engine = get_engine()
table_name = "enriched_pubmed_data"
chunk_size = 10000

def main():
    print("Loading from DB...")
    pubmed_df = pd.read_sql("SELECT * FROM pubmed_test", engine)
    apc_df = pd.read_sql("SELECT * FROM openapc_test", engine)
    doaj_df = pd.read_sql("SELECT * FROM doaj_test", engine)

    print("Enriching...")
    start = time.time()
    pubmed_df, counts = enrich_pubmed(pubmed_df, apc_df, doaj_df)
    print(f"Done in {round(time.time() - start, 2)}s")

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        pmid TEXT,
        title TEXT,
        doi TEXT,
        issn TEXT,
        year INTEGER,
        journal TEXT,
        authors TEXT,
        affiliations TEXT,
        country TEXT,
        cost_price_eur FLOAT,
        estimated_price_eur FLOAT,
        total_price_eur FLOAT,
        match_source TEXT
    );
    """

    # Drop and recreate the table before upload , because the data could be changed
    with engine.begin() as conn:
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        conn.execute(text(create_table_sql))

    # to db
    print("Uploading enriched data...")
    for i in tqdm(range(0, len(pubmed_df), chunk_size), desc="Uploading"):
        try:
            pubmed_df.iloc[i:i+chunk_size].to_sql(table_name, con=engine, if_exists="append", index=False)
        except SQLAlchemyError as e:
            print(f"Upload failed at chunk {i}: {e}")
            break

    print("\nMatch Summary:")
    total = len(pubmed_df)
    for k, v in counts.items():
        print(f"  {k}: {v} ({v/total:.2%})")

if __name__ == "__main__":
    main()
