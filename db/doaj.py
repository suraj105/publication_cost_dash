import pandas as pd
import logging
from sqlalchemy import text
from db.db_config import get_engine
from db.constants import EU_COUNTRIES
from db.db import save_to_postgres
from utils.utils import convert_to_eur,extract_currency,extract_number
import os

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("doaj_loader")

# initial db engine
engine = get_engine()
TABLE_NAME = "doaj"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
INPUT_CSV = os.path.join(BASE_DIR, "data", "journalcsv__doaj_20250718_0928_utf8.csv")

def main():
    #reading doaj file
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    df["Added on Date"] = pd.to_datetime(df["Added on Date"], errors="coerce")
    df = df.dropna(subset=["Country of publisher"])
    #filtering for eu countries and year 2024
    filtered_df = df[
        (df["Added on Date"].dt.year == 2024) &
        (df["Country of publisher"].isin(EU_COUNTRIES))
    ].copy()

    filtered_df["original_amount"] = filtered_df["APC amount"].apply(extract_number)
    filtered_df["original_currency"] = filtered_df["APC amount"].apply(extract_currency)
    filtered_df["amount_eur"] = filtered_df.apply(
        lambda row: convert_to_eur(row["original_amount"], row["original_currency"]),
        axis=1
    )

    result_df = pd.DataFrame({
        "pmid": "",
        "title": filtered_df["Journal title"],
        "doi": "",
        "issn": filtered_df["Journal ISSN (print version)"].fillna(""),
        "eissn": filtered_df["Journal EISSN (online version)"].fillna(""),
        "year": filtered_df["Added on Date"].dt.year,
        "journal": filtered_df["Journal title"],
        "authors": "",
        "affiliations": "",
        "country": filtered_df["Country of publisher"],
        "original_amount": filtered_df["original_amount"],
        "original_currency": filtered_df["original_currency"],
        "amount_eur": filtered_df["amount_eur"]
    })

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        pmid TEXT,
        title TEXT,
        doi TEXT,
        issn TEXT,
        eissn TEXT,
        year INTEGER,
        journal TEXT,
        authors TEXT,
        affiliations TEXT,
        country TEXT,
        original_amount FLOAT,
        original_currency TEXT,
        amount_eur FLOAT
    );
    """

    with engine.begin() as conn:
        conn.execute(text(create_table_sql))

    save_to_postgres(result_df, engine, TABLE_NAME, create_sql=create_table_sql, logger=logger)


if __name__ == "__main__":
    main()
