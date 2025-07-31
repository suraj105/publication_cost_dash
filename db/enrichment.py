# enrichment.py

import pandas as pd
from tqdm import tqdm

# enrichment logic with help of pubmed,openapc and doaj
def enrich_pubmed(pubmed_df, apc_df, doaj_df):
    from utils.utils import safe_float, normalize

    # normalise for consistent matching
    pubmed_df["doi"] = normalize(pubmed_df["doi"])
    pubmed_df["issn"] = normalize(pubmed_df["issn"])

    apc_df["doi"] = normalize(apc_df["doi"])
    apc_df["issn"] = normalize(apc_df["issn"])
    apc_df["year"] = pd.to_numeric(apc_df["year"], errors="coerce")

    doaj_df["doi"] = normalize(doaj_df["doi"])
    doaj_df["issn"] = normalize(doaj_df["issn"])
    doaj_df["eissn"] = normalize(doaj_df["eissn"])
    doaj_df["amount_eur"] = pd.to_numeric(doaj_df["amount_eur"], errors="coerce")

    apc_doi_lookup = apc_df.set_index("doi")["euro"].to_dict()
    doaj_doi_lookup = doaj_df.set_index("doi")["amount_eur"].dropna().to_dict()

    # initialize target column
    pubmed_df["cost_price_eur"] = None
    pubmed_df["estimated_price_eur"] = None
    pubmed_df["total_price_eur"] = None
    pubmed_df["match_source"] = "none"

    counts = {"doi_openapc": 0, "doi_doaj": 0, "issn_openapc": 0, "issn_doaj": 0, "none": 0}

    # loop over each row for enriching
    for idx, row in tqdm(pubmed_df.iterrows(), total=len(pubmed_df), desc=" Enriching"):
        year = int(row["year"]) if not pd.isna(row["year"]) else 2024
        doi = row["doi"]
        issn = row.get("issn", "").strip().lower()

        # match by doi in openapc
        if doi in apc_doi_lookup:
            price = round(apc_doi_lookup[doi], 2)
            pubmed_df.at[idx, "cost_price_eur"] = price
            pubmed_df.at[idx, "total_price_eur"] = price
            pubmed_df.at[idx, "match_source"] = "doi_openapc"
            counts["doi_openapc"] += 1
            continue

        # match by doi in doaj
        if doi in doaj_doi_lookup:
            price = round(doaj_doi_lookup[doi], 2)
            pubmed_df.at[idx, "cost_price_eur"] = price
            pubmed_df.at[idx, "total_price_eur"] = price
            pubmed_df.at[idx, "match_source"] = "doi_doaj"
            counts["doi_doaj"] += 1
            continue

        # estimate via issn
        if issn:
            matches = apc_df[apc_df["issn"] == issn].copy()
            if not matches.empty:
                matches["year_diff"] = matches["year"] - year
                before = matches[matches["year_diff"] < 0]
                after = matches[matches["year_diff"] > 0]
                same_year = matches[matches["year_diff"] == 0]

                if not before.empty and not after.empty:
                    est = (before.loc[before["year_diff"].idxmax()]["euro"] +
                           after.loc[after["year_diff"].idxmin()]["euro"]) / 2
                elif not same_year.empty:
                    est = same_year["euro"].mean()
                else:
                    matches["abs_diff"] = abs(matches["year_diff"])
                    est = matches.loc[matches["abs_diff"].idxmin()]["euro"]

                pubmed_df.at[idx, "estimated_price_eur"] = round(est, 2)
                pubmed_df.at[idx, "total_price_eur"] = round(est, 2)
                pubmed_df.at[idx, "match_source"] = "issn_openapc"
                counts["issn_openapc"] += 1
                continue

            # fallback by issn or eissn in doaj
            doaj_match = doaj_df[(doaj_df["issn"] == issn) | (doaj_df["eissn"] == issn)]
            if not doaj_match.empty:
                est = doaj_match["amount_eur"].dropna().mean()
                pubmed_df.at[idx, "cost_price_eur"] = round(est, 2)
                pubmed_df.at[idx, "total_price_eur"] = round(est, 2)
                pubmed_df.at[idx, "match_source"] = "issn_doaj"
                counts["issn_doaj"] += 1
                continue

        # count for no match , so that later it can be tracked for unmatched issn
        counts["none"] += 1

    pubmed_df["cost_price_eur"] = pubmed_df["cost_price_eur"].apply(safe_float)
    pubmed_df["estimated_price_eur"] = pubmed_df["estimated_price_eur"].apply(safe_float)
    pubmed_df["total_price_eur"] = pubmed_df["total_price_eur"].apply(safe_float)

    return pubmed_df, counts
