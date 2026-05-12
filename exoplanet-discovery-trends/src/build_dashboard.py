"""
Assemble all six Plotly charts into a self-contained dashboard HTML file.
Output: outputs/dashboard.html
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from fetch_data import CACHE_PATH
from process import load_and_process
from visualize import (
    build_method_colors,
    fig_annual_bar,
    fig_cumulative,
    fig_method_share,
    fig_orbital_scatter,
    fig_pre_post_kepler,
    fig_top_facilities,
)

OUTPUT_PATH = ROOT / "outputs" / "dashboard.html"

CHART_CAPTIONS = [
    (
        "Cumulative Exoplanet Discoveries by Detection Method",
        "Transit method's compounding effect post-2009 is unmistakable. "
        "The slope steepens sharply after Kepler's first data release, "
        "while radial velocity growth flattens into a near-plateau.",
    ),
    (
        "Annual Exoplanet Discoveries by Detection Method",
        "The 2009-2018 Kepler era produced a step-change in discovery volume. "
        "Single-year peaks in 2014 and 2016 reflect catalog validation releases, "
        "not real-time detections.",
    ),
    (
        "Detection Method Share Over Time",
        "Before Kepler, radial velocity accounted for more than 80 percent of all confirmed discoveries. "
        "By 2020, transit detections make up over 75 percent of the annual total.",
    ),
    (
        "Top 15 Discovery Facilities",
        "NASA's Kepler and TESS missions together account for the majority of all confirmed detections. "
        "Ground-based facilities fill in the gaps for bright, nearby systems.",
    ),
    (
        "Orbital Period vs Planet Radius",
        "Hot Jupiters cluster in the lower-left corner, with short periods and large radii. "
        "The upper-right void reflects a detection limit: long-period, Earth-sized planets "
        "remain difficult to confirm.",
    ),
    (
        "Average Annual Transit Discoveries by Mission Era",
        "Average annual transit confirmations grew from roughly 10 per year before Kepler "
        "to over 300 per year in the TESS era. "
        "That is a 30x increase driven almost entirely by space-based photometry.",
    ),
]

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #ffffff;
    color: #1a1a2e;
    line-height: 1.6;
}
header {
    background: #0f3460;
    color: #ffffff;
    padding: 2.5rem 2rem 2rem;
    text-align: center;
}
header h1 {
    font-size: clamp(1.4rem, 3vw, 2.2rem);
    font-weight: 700;
    letter-spacing: -0.02em;
}
header p {
    margin-top: 0.5rem;
    font-size: 1rem;
    opacity: 0.82;
}
.container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 1.5rem 1.5rem 4rem;
}
.chart-section {
    margin: 3rem 0;
    padding-bottom: 2.5rem;
    border-bottom: 1px solid #e8e8f0;
}
.chart-section:last-child {
    border-bottom: none;
}
.chart-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #0f3460;
    margin-bottom: 0.75rem;
}
.caption {
    font-size: 0.9rem;
    color: #555;
    margin-top: 0.75rem;
    max-width: 780px;
    line-height: 1.65;
}
footer {
    text-align: center;
    padding: 1.5rem;
    font-size: 0.8rem;
    color: #aaa;
    border-top: 1px solid #e8e8f0;
}
"""


def _fig_to_div(fig, first: bool = False) -> str:
    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if first else False,
        config={"displayModeBar": True, "responsive": True},
    )


def build(refresh: bool = False, data: dict = None) -> None:
    if data is None:
        data = load_and_process(CACHE_PATH)
    df_raw = data["df_raw"]
    df_dated = data["df_dated"]

    year_min = int(df_dated["disc_year"].min())
    year_max = int(df_dated["disc_year"].max())
    total = len(df_raw)

    all_methods = list(data["df_annual"].columns)
    method_colors = build_method_colors(all_methods)

    figures = [
        fig_cumulative(data["df_cumulative"], method_colors),
        fig_annual_bar(data["df_annual"], method_colors),
        fig_method_share(data["df_share"], method_colors),
        fig_top_facilities(data["df_facilities"]),
        fig_orbital_scatter(data["df_scatter"], method_colors),
        fig_pre_post_kepler(data["df_prepost"]),
    ]

    chart_blocks = []
    for i, (fig, (title, caption)) in enumerate(zip(figures, CHART_CAPTIONS)):
        div = _fig_to_div(fig, first=(i == 0))
        chart_blocks.append(
            f'<div class="chart-section">'
            f'<div class="chart-title">{title}</div>'
            f"{div}"
            f'<p class="caption">{caption}</p>'
            f"</div>"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Exoplanet Discovery Trends</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <h1>Exoplanet Discovery Trends</h1>
  <p>NASA Exoplanet Archive Analysis &middot; {total:,} confirmed planets &middot; {year_min}&ndash;{year_max}</p>
</header>
<div class="container">
{"".join(chart_blocks)}
</div>
<footer>
  Data: NASA Exoplanet Archive (pscomppars table) &middot;
  Built with Python, Pandas and Plotly &middot;
  <a href="https://siddhesh.org" style="color:#999">siddhesh.org</a>
</footer>
</body>
</html>"""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"[dash]    Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    build(refresh=args.refresh)
