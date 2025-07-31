# utils.py
import re
import pandas as pd
from db.constants import CURRENCY_RATES_TO_EUR

def normalize(series):
    """Lowercase and strip a pandas Series (typically for DOIs, ISSNs)."""
    return series.astype(str).str.lower().str.strip()

def normalize_country(series):
    """Standardize country names: title-case and strip whitespace."""
    return series.astype(str).str.strip().str.title()

# safely convert a value to float
def safe_float(val):
    try:
        if pd.isna(val):
            return None
        return float(val)
    except:
        return None

# extracts currencly like PLN or USD
def extract_currency(value):
    if isinstance(value, str):
        match = re.search(r"\b([A-Z]{3})\b", value)
        return match.group(1) if match else "EUR"
    return "EUR"

# for extractsíng number
def extract_number(value):
    if isinstance(value, str):
        cleaned = re.findall(r"[\d.,]+", value)
        if cleaned:
            try:
                return float(cleaned[0].replace(",", ""))
            except:
                return None
    return None

# to convert foreign currencies to euro
def convert_to_eur(amount, currency):
    if pd.isna(amount) or currency not in CURRENCY_RATES_TO_EUR:
        return None
    return round(amount * CURRENCY_RATES_TO_EUR[currency], 2)
