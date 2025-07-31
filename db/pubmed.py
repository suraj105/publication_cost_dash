import os
import pandas as pd
from glob import glob
from tqdm import tqdm
from db.db_config import get_engine
from db.constants import EU_COUNTRIES
from utils.utils import normalize_country
from db.db import save_to_postgres

# initialize db engine
engine = get_engine()
TABLE_NAME = "pubmed"
CHUNK_SIZE = 10000


# Loads xml files which were downloaded and parsed to xml from https://ftp.ncbi.nlm.nih.gov/pubmed/basefile/ , the script lies in utils.download_pubmed_gz.py

# comnines and filter data according to country and year
def combine_and_filter_pubmed(input_folder):
    all_files = glob(os.path.join(input_folder, '*.csv'))
    combined_df = pd.DataFrame()

    print(f"Found {len(all_files)} CSV files in {input_folder}")
    for file in tqdm(all_files, desc="🔍 Filtering PubMed CSVs"):
        try:
            df = pd.read_csv(file, dtype=str)
            if 'year' not in df.columns or 'country' not in df.columns:
                print(f"Skipping {file} (missing 'year' or 'country')")
                continue

            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            df['country'] = normalize_country(df['country'])

            filtered_df = df[
                (df['year'] == 2024) &
                (df['country'].isin(EU_COUNTRIES))
            ]
            combined_df = pd.concat([combined_df, filtered_df], ignore_index=True)

        except Exception as e:
            print(f"Error processing {file}: {e}")

    print(f"\nFiltered {len(combined_df)} entries from PubMed")
    return combined_df

create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    pmid TEXT,
    title TEXT,
    doi TEXT,
    issn TEXT,
    year INTEGER,
    journal TEXT,
    authors TEXT,
    affiliations TEXT,
    country TEXT
);
"""

def main():
    input_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "pubmed_raw_to_csv"))
    df = combine_and_filter_pubmed(input_folder)
    save_to_postgres(
        df,
        engine,
        TABLE_NAME,
        create_sql=create_table_sql,
        clear_existing=True,
        chunk_size=10000
    )
if __name__ == "__main__":
    main()
