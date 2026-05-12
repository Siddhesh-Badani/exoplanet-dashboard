"""
Load and process the exoplanet CSV into analysis-ready DataFrames.
Returns a dict of tidy DataFrames keyed by name.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = ROOT / "data" / "exoplanets_cached.csv"

NUMERIC_COLS = ["sy_dist", "pl_orbper", "pl_rade", "pl_bmasse", "st_teff"]
STRING_COLS = ["discoverymethod", "disc_facility", "disc_telescope", "hostname"]


def _decade_label(year) -> str:
    if pd.isna(year):
        return "Unknown"
    decade = int(year) // 10 * 10
    return f"{decade}s"


def _mission_era(year) -> str:
    if pd.isna(year):
        return "Unknown"
    y = int(year)
    if y < 2009:
        return "Pre-Kepler"
    if y <= 2017:
        return "Kepler Era"
    return "TESS Era"


def load_and_process(csv_path: Path = CACHE_PATH) -> dict:
    df = pd.read_csv(csv_path, low_memory=False)

    # Numeric columns: coerce, keep NaN
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # String columns: fill Unknown
    for col in STRING_COLS:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    # disc_year: nullable integer
    df["disc_year"] = pd.to_numeric(df["disc_year"], errors="coerce")

    # Feature engineering
    df["decade_bin"] = df["disc_year"].apply(_decade_label)
    df["mission_era"] = df["disc_year"].apply(_mission_era)

    # Normalize method names for consistent display
    method_map = {
        "transit": "Transit",
        "radial velocity": "Radial Velocity",
        "imaging": "Imaging",
        "microlensing": "Microlensing",
        "transit timing variations": "Transit Timing Variations",
        "eclipse timing variations": "Eclipse Timing Variations",
        "astrometry": "Astrometry",
        "orbital brightness modulation": "Orbital Brightness Modulation",
        "pulsation timing variations": "Pulsation Timing Variations",
        "pulsar timing": "Pulsar Timing",
        "disk kinematics": "Disk Kinematics",
    }
    df["discoverymethod"] = (
        df["discoverymethod"]
        .str.strip()
        .str.lower()
        .map(method_map)
        .fillna(df["discoverymethod"].str.strip())
    )

    # Drop rows with no disc_year for time-series aggregations
    df_dated = df.dropna(subset=["disc_year"]).copy()
    df_dated["disc_year"] = df_dated["disc_year"].astype(int)

    # Annual counts: pivot [year x method]
    annual_counts = (
        df_dated.groupby(["disc_year", "discoverymethod"])
        .size()
        .reset_index(name="count")
    )
    df_annual = annual_counts.pivot(
        index="disc_year", columns="discoverymethod", values="count"
    ).fillna(0)

    # Cumulative discoveries per method
    df_cumulative = df_annual.cumsum()

    # YoY growth rate
    df_growth = df_annual.pct_change() * 100

    # Normalized method share per year
    row_totals = df_annual.sum(axis=1)
    df_share = df_annual.div(row_totals, axis=0).fillna(0)

    # Top 15 facilities
    facility_counts = (
        df.groupby("disc_facility")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(15)
    )
    facility_counts = facility_counts[facility_counts["disc_facility"] != "Unknown"]
    df_facilities = facility_counts.head(15)

    # Scatter data: valid orbital period and radius
    df_scatter = df.dropna(subset=["pl_orbper", "pl_rade"]).copy()
    df_scatter = df_scatter[df_scatter["pl_orbper"] > 0]
    df_scatter = df_scatter[df_scatter["pl_rade"] > 0]

    # Pre/post Kepler transit comparison
    transit_df = df_dated[df_dated["discoverymethod"] == "Transit"].copy()
    era_annual = (
        transit_df.groupby(["mission_era", "disc_year"])
        .size()
        .reset_index(name="count")
    )
    era_order = ["Pre-Kepler", "Kepler Era", "TESS Era"]
    df_prepost = (
        era_annual.groupby("mission_era")["count"]
        .mean()
        .reindex(era_order)
        .reset_index()
    )
    df_prepost.columns = ["mission_era", "avg_annual_transit"]

    print("[process] Feature engineering complete")
    return {
        "df_raw": df,
        "df_dated": df_dated,
        "df_annual": df_annual,
        "df_cumulative": df_cumulative,
        "df_growth": df_growth,
        "df_share": df_share,
        "df_facilities": df_facilities,
        "df_scatter": df_scatter,
        "df_prepost": df_prepost,
    }
