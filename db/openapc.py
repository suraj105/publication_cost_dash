import pandas as pd
import requests
import logging
from io import StringIO
from db.db_config import get_engine
from db.db import save_to_postgres


# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("openapc_loader")

# initialize db engine
engine = get_engine()
TABLE_NAME = "openapc"


# OpenAPC dataset URL
OPENAPC_CSV_URL = "https://raw.githubusercontent.com/OpenAPC/openapc-de/master/data/apc_de.csv"

def download_openapc_full():
    logger.info("Downloading OpenAPC dataset...")
    try:
        r = requests.get(OPENAPC_CSV_URL, timeout=60)
        r.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to download OpenAPC CSV: {e}")
        return pd.DataFrame()

    df = pd.read_csv(StringIO(r.text), low_memory=False)
    logger.info(f"Loaded {len(df)} total entries")

    df['period'] = pd.to_numeric(df['period'], errors='coerce')

    df = df[[
        'doi', 'pmid', 'euro', 'period', 'journal_full_title',
        'institution', 'issn', 'issn_print', 'issn_electronic', 'issn_l'
    ]].rename(columns={
        'period': 'year',
        'journal_full_title': 'journal'
    })
    return df

def main():
    df = download_openapc_full()
    save_to_postgres(df, engine, TABLE_NAME, if_exists="replace", logger=logger)

if __name__ == "__main__":
    main()
