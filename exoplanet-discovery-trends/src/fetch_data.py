"""
Fetch confirmed exoplanet data from NASA Exoplanet Archive TAP API.
Caches result to data/exoplanets_cached.csv. Use --refresh to force re-fetch.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CACHE_PATH = DATA_DIR / "exoplanets_cached.csv"

TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

ADQL_QUERY = (
    "SELECT pl_name,hostname,disc_year,discoverymethod,disc_facility,"
    "disc_telescope,sy_dist,pl_orbper,pl_rade,pl_bmasse,st_teff "
    "FROM pscomppars"
)


def fetch(refresh: bool = False) -> pd.DataFrame:
    if CACHE_PATH.exists() and not refresh:
        print(f"[fetch]   Using cache: {CACHE_PATH}")
        df = pd.read_csv(CACHE_PATH, low_memory=False)
    else:
        print("[fetch]   Querying NASA Exoplanet Archive TAP API...")
        response = requests.get(
            TAP_URL,
            params={"query": ADQL_QUERY, "format": "csv"},
            timeout=120,
        )
        response.raise_for_status()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(response.text, encoding="utf-8")
        df = pd.read_csv(CACHE_PATH, low_memory=False)
        print(f"[fetch]   Saved to {CACHE_PATH}")

    year_col = df["disc_year"].dropna()
    year_min = int(year_col.min())
    year_max = int(year_col.max())
    print(f"[fetch]   {len(df):,} planets loaded | {year_min}-{year_max}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Fetch NASA exoplanet data")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-fetch even if cache exists",
    )
    args = parser.parse_args()
    fetch(refresh=args.refresh)


if __name__ == "__main__":
    main()
