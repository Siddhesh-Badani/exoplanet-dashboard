# Exoplanet Discovery Trends

A data analytics project that surfaces 35 years of planetary detection history using real data from NASA's Exoplanet Archive. The visual output answers one central question: how did Kepler, K2 and TESS reshape the rate and method of exoplanet discovery?

---

## Why This Exists

Before 2009, finding a planet outside our solar system was a years-long project involving ground-based spectrographs and careful follow-up. After Kepler launched, the field changed almost overnight. This project makes that shift visible, tracing how detection methods evolved, which missions drove the acceleration and where the catalog stands today.

---

## Key Findings

- 6,286 confirmed exoplanets are in the NASA archive, spanning 1992 through 2026.
- Transit photometry accounts for 4,646 of those discoveries, roughly 74 percent of the total. Radial velocity contributes another 1,180, or about 19 percent.
- Average annual transit discoveries grew from fewer than 10 per year before Kepler to over 300 per year in the TESS era. That is a 30x increase driven almost entirely by space-based photometry.
- NASA's Kepler and TESS missions account for the majority of all confirmed planets. No ground-based facility comes close.
- Radial velocity dominated exoplanet science through the 2000s, exceeding 80 percent of annual detections as late as 2008. By 2020 that share had fallen below 10 percent.

---

## Tech Stack

- **Python 3.11+**
- **Pandas 2.2** for data processing and aggregation
- **Plotly 5.22** for interactive visualizations
- **Requests** for NASA TAP API queries
- **Jupyter** for exploratory analysis
- **Pure HTML/CSS** for dashboard and story layouts

---

## Project Structure

```
exoplanet-discovery-trends/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py                        entry point, runs full pipeline
├── data/
│   └── exoplanets_cached.csv      auto-generated
├── src/
│   ├── __init__.py
│   ├── fetch_data.py              NASA TAP API query and cache
│   ├── process.py                 cleaning, feature engineering
│   ├── visualize.py               six reusable Plotly figure functions
│   ├── build_dashboard.py         assembles outputs/dashboard.html
│   └── build_story.py             assembles outputs/story.html
├── outputs/
│   ├── dashboard.html             auto-generated
│   └── story.html                 auto-generated
└── notebooks/
    └── eda.ipynb                  exploratory analysis
```

---

## How to Run

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Fetch data from NASA Exoplanet Archive**

```bash
python src/fetch_data.py
```

Add `--refresh` to force a re-fetch even if the cache already exists.

**3. Build the interactive dashboard**

```bash
python src/build_dashboard.py
```

Opens `outputs/dashboard.html` in any browser. No server required.

**4. Build the visual story**

```bash
python src/build_story.py
```

Opens `outputs/story.html` in any browser. No server required.

**Run everything at once**

```bash
python main.py
```

---

## Data Source

NASA Exoplanet Archive, Planetary Systems Composite Parameters table (`pscomppars`).

Queried via TAP API: `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`

Citation: NASA Exoplanet Archive. (2024). Planetary Systems. IPAC. https://doi.org/10.26133/NEA12

---


## Author

Siddhesh Badani — [siddhesh.org](https://siddhesh.org)
