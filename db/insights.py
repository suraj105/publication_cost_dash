from db.db import load_data_from_db
from utils.utils import normalize

# for unmatched issn, from which it will be easier to input manul entry for most repeated issn
def top_unmatched_issns():
    df = load_data_from_db()

    df["match_source"] = normalize(df["match_source"])
    df["issn"] = normalize(df["issn"])

    filtered = df[
        (df["match_source"].isin(["none", "unmatched"])) &
        (df["total_price_eur"].isna()) &
        df["issn"].notna() &
        (df["issn"] != "")
    ]

    top_issns = filtered["issn"].value_counts().head(10).reset_index()
    top_issns.columns = ["issn", "count"]
    return top_issns
