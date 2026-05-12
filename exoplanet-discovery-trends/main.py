"""
Full pipeline entry point. Fetches data, builds dashboard and story.
Usage:
    python main.py          # use cache if present
    python main.py --refresh  # force re-fetch from NASA API
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from build_dashboard import build as build_dashboard
from build_story import build as build_story
from fetch_data import CACHE_PATH, fetch
from process import load_and_process


def main():
    parser = argparse.ArgumentParser(description="Build the Exoplanet Discovery Trends project")
    parser.add_argument("--refresh", action="store_true", help="Force re-fetch from NASA API")
    args = parser.parse_args()

    fetch(refresh=args.refresh)
    data = load_and_process(CACHE_PATH)
    build_dashboard(refresh=args.refresh, data=data)
    build_story(data=data)

    df_raw = data["df_raw"]
    df_dated = data["df_dated"]
    total = len(df_raw)
    year_min = int(df_dated["disc_year"].min())
    year_max = int(df_dated["disc_year"].max())

    method_counts = (
        df_dated.groupby("discoverymethod")
        .size()
        .sort_values(ascending=False)
        .head(3)
    )
    top3 = ", ".join(f"{m} ({n:,})" for m, n in method_counts.items())

    dash_path = ROOT / "outputs" / "dashboard.html"
    story_path = ROOT / "outputs" / "story.html"

    print()
    print("── Summary " + "─" * 38)
    print(f"Total planets  : {total:,}")
    print(f"Year range     : {year_min}-{year_max}")
    print(f"Top methods    : {top3}")
    print(f"Dashboard      : {dash_path}")
    print(f"Story          : {story_path}")
    print("─" * 48)


if __name__ == "__main__":
    main()
