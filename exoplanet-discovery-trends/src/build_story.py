"""
Build the scroll-based visual story page.
Output: outputs/story.html
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

OUTPUT_PATH = ROOT / "outputs" / "story.html"

CSS = """
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    margin: 0;
    font-family: Georgia, "Times New Roman", serif;
    background: #fafaf8;
    color: #1c1c1c;
    line-height: 1.75;
}
nav {
    position: sticky;
    top: 0;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(6px);
    border-bottom: 1px solid #e0e0d8;
    padding: 0.6rem 1.5rem;
    z-index: 100;
    display: flex;
    gap: 1.5rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 0.8rem;
    flex-wrap: wrap;
}
nav a {
    color: #555;
    text-decoration: none;
    transition: color 0.2s;
}
nav a:hover { color: #0f3460; }
.hero {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    color: #fff;
    padding: 5rem 1.5rem 4rem;
    text-align: center;
}
.hero h1 {
    font-size: clamp(1.8rem, 5vw, 3rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    margin-bottom: 1rem;
}
.hero p {
    max-width: 600px;
    margin: 0 auto;
    font-size: 1.1rem;
    opacity: 0.85;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.6;
}
.chapter {
    max-width: 800px;
    margin: 0 auto;
    padding: 4rem 1.5rem;
    border-bottom: 1px solid #e8e8e0;
}
.chapter:last-child { border-bottom: none; }
.chapter-label {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #0f3460;
    margin-bottom: 0.5rem;
}
.chapter h2 {
    font-size: clamp(1.4rem, 3vw, 2rem);
    font-weight: 700;
    line-height: 1.25;
    margin-bottom: 1.25rem;
    color: #111;
}
.chapter p {
    font-size: 1.05rem;
    margin-bottom: 1rem;
    color: #2a2a2a;
}
.stat-callout {
    background: #f0f4ff;
    border-left: 4px solid #0f3460;
    padding: 1rem 1.25rem;
    margin: 1.75rem 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 1rem;
    color: #0f3460;
    font-weight: 500;
    line-height: 1.5;
    border-radius: 0 6px 6px 0;
}
.chart-container {
    margin: 2rem -1rem;
    max-width: calc(100vw - 1rem);
}
@media (min-width: 960px) {
    .chart-container {
        margin: 2rem -80px;
        max-width: 960px;
    }
}
footer {
    text-align: center;
    padding: 2.5rem 1.5rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 0.85rem;
    color: #888;
    background: #f5f5f0;
    border-top: 1px solid #e0e0d8;
}
footer a { color: #666; }
"""

CHAPTERS = [
    {
        "id": "quiet-decade",
        "label": "Chapter One",
        "title": "The Quiet Decade",
        "narrative": """
<p>The search for worlds beyond our solar system is older than most people realize.
By the late 1980s, astronomers suspected that other stars harbored planets,
but confirming a detection was another matter. The tools were crude and the noise overwhelming.</p>
<p>The first confirmed exoplanet discovery came in 1992, orbiting a pulsar called PSR 1257+12.
Two years later, the first planet around a sun-like star was announced.
For the rest of the decade, each new discovery was a headline event. They came slowly,
one or two a year, hard-won through patient radial velocity surveys.</p>
<p>By 1999, fewer than 30 confirmed exoplanets existed.
The chart below captures that era: thin columns, long stretches of near-silence,
and the unmistakable sense of a field still finding its footing.</p>
""",
        "stat": "By 1999, fewer than 30 exoplanets had been confirmed. Most took years of follow-up observation to validate.",
        "chart": "annual_bar",
    },
    {
        "id": "doppler-era",
        "label": "Chapter Two",
        "title": "The Doppler Era",
        "narrative": """
<p>Through the 2000s, radial velocity, the Doppler wobble method, dominated exoplanet science.
The idea is straightforward: a planet's gravity tugs its host star toward and away from us,
shifting the star's spectral lines in a measurable pattern.
With enough precision, you can infer the planet's mass and orbital period.</p>
<p>Ground-based spectrographs like HIRES and HARPS pushed detection limits lower each year.
The team at Geneva Observatory catalogued hundreds of nearby stellar systems.
By 2008, radial velocity accounted for more than 80 percent of all known exoplanets.</p>
<p>It was powerful work, but it had a ceiling. Radial velocity favors massive planets close to their stars.
Earth-sized planets in habitable zones were mostly beyond reach.
The field needed a different approach, one that could survey thousands of stars at once.</p>
""",
        "stat": "In 2008, radial velocity accounted for over 80 percent of all confirmed exoplanet discoveries.",
        "chart": "method_share",
    },
    {
        "id": "kepler",
        "label": "Chapter Three",
        "title": "Kepler Changes Everything",
        "narrative": """
<p>NASA's Kepler Space Telescope launched in March 2009 and pointed at a single patch of sky
for four continuous years. Its job was to watch 150,000 stars simultaneously,
looking for the faint dimming that happens when a planet crosses in front of its host star.
The transit method had been used before, but never at this scale.</p>
<p>The results were staggering. Within a few years, Kepler had identified thousands of planet candidates.
Catalog validation releases in 2014 and 2016 each confirmed hundreds of planets in a single announcement.
Annual discovery counts jumped from double digits to triple digits almost overnight.</p>
<p>More than raw numbers, Kepler reshaped our picture of the galaxy.
Small rocky planets were common. Multi-planet systems were the rule, not the exception.
The universe, it turned out, was full of worlds.</p>
""",
        "stat": "Average annual transit discoveries grew from fewer than 10 per year before Kepler to over 300 per year in the TESS era.",
        "chart": "pre_post_kepler",
    },
    {
        "id": "k2-tess",
        "label": "Chapter Four",
        "title": "K2 and TESS",
        "narrative": """
<p>Kepler lost a second reaction wheel in 2013, ending its original staring mission.
Engineers found a workaround: by using solar pressure to stabilize the spacecraft,
they could observe new fields of sky every 80 days. The repurposed mission, called K2,
extended Kepler's life by four more years and added thousands more planets to the catalog.</p>
<p>In 2018, the Transiting Exoplanet Survey Satellite launched. Where Kepler stared at one patch,
TESS surveys the entire sky in two-year cycles, focusing on bright, nearby stars
that are easier to follow up from the ground. It is a different kind of catalog:
shallower in depth but far wider in reach.</p>
<p>Together, K2 and TESS kept the momentum going after Kepler's retirement in 2018.
The cumulative count continued its steep climb, now distributed across a far larger
portion of the sky.</p>
""",
        "stat": "Transit detections account for over 75 percent of all confirmed exoplanets as of 2024, up from under 10 percent in 2005.",
        "chart": "cumulative",
    },
    {
        "id": "now",
        "label": "Chapter Five",
        "title": "Where We Are Now",
        "narrative": """
<p>More than 5,000 exoplanets are confirmed as of 2024. The archive spans gas giants larger than Jupiter,
rocky worlds smaller than Earth, scorching hot Neptunes, and cold super-Earths in distant orbits.
The parameter space is vast, and we have only sampled a fraction of it.</p>
<p>The distribution of confirmed planets tells a story about our methods as much as about the galaxy.
Hot Jupiters, large and close-in, were easy to find first. Small rocky planets at longer periods
are harder to confirm and are systematically under-represented in the current catalog.</p>
<p>The next decade will belong to the James Webb Space Telescope and ground-based extremely large telescopes.
The science is shifting from detection to characterization: what are these atmospheres made of,
and do any of them look like ours?</p>
""",
        "stat": "Over 5,000 confirmed exoplanets in the archive. The vast majority were found in the last 15 years.",
        "chart": "orbital_scatter",
    },
]

NAV_ITEMS = [
    ("quiet-decade", "The Quiet Decade"),
    ("doppler-era", "The Doppler Era"),
    ("kepler", "Kepler Changes Everything"),
    ("k2-tess", "K2 and TESS"),
    ("now", "Where We Are Now"),
]


def _fig_to_div(fig, first: bool = False) -> str:
    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if first else False,
        config={"displayModeBar": True, "responsive": True},
    )


def build(data: dict = None) -> None:
    if data is None:
        data = load_and_process(CACHE_PATH)
    df_raw = data["df_raw"]
    df_dated = data["df_dated"]

    year_min = int(df_dated["disc_year"].min())
    year_max = int(df_dated["disc_year"].max())
    total = len(df_raw)

    all_methods = list(data["df_annual"].columns)
    method_colors = build_method_colors(all_methods)

    chart_registry = {
        "annual_bar": fig_annual_bar(data["df_annual"], method_colors),
        "method_share": fig_method_share(data["df_share"], method_colors),
        "pre_post_kepler": fig_pre_post_kepler(data["df_prepost"]),
        "cumulative": fig_cumulative(data["df_cumulative"], method_colors),
        "orbital_scatter": fig_orbital_scatter(data["df_scatter"], method_colors),
    }

    nav_html = "\n".join(
        f'<a href="#{ch_id}">{label}</a>' for ch_id, label in NAV_ITEMS
    )

    first_chart_rendered = False
    chapter_blocks = []
    for ch in CHAPTERS:
        fig = chart_registry[ch["chart"]]
        chart_div = _fig_to_div(fig, first=not first_chart_rendered)
        first_chart_rendered = True

        chapter_blocks.append(
            f'<section class="chapter" id="{ch["id"]}">'
            f'<div class="chapter-label">{ch["label"]}</div>'
            f'<h2>{ch["title"]}</h2>'
            f'{ch["narrative"]}'
            f'<div class="stat-callout">{ch["stat"]}</div>'
            f'<div class="chart-container">{chart_div}</div>'
            f"</section>"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Exoplanet Discovery: A Visual Story</title>
<style>{CSS}</style>
</head>
<body>

<nav>
  <strong style="font-family:-apple-system,sans-serif;font-size:0.8rem;color:#0f3460;margin-right:0.5rem;">Exoplanet Discovery</strong>
  {nav_html}
</nav>

<div class="hero">
  <h1>How We Found 5,000 Worlds</h1>
  <p>A visual history of exoplanet discovery, from the first faint signals in the 1990s
  to the flood of detections that followed Kepler's launch.
  {total:,} confirmed planets, {year_min}&ndash;{year_max}.</p>
</div>

{"".join(chapter_blocks)}

<footer>
  Data: NASA Exoplanet Archive (pscomppars) &middot;
  Analysis and visualization by <a href="https://siddhesh.org">Siddhesh Badani</a> &middot;
  Built with Python, Pandas and Plotly
</footer>

</body>
</html>"""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"[story]   Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
