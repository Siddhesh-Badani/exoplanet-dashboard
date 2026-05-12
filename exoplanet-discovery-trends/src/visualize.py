"""
Reusable Plotly figure factory for exoplanet discovery analysis.
Each function accepts processed DataFrames and returns a go.Figure.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

VIVID = px.colors.qualitative.Vivid

# Mission event annotations
MISSION_EVENTS = [
    {"year": 2009, "label": "Kepler launch", "color": "#555"},
    {"year": 2014, "label": "K2 begins", "color": "#777"},
    {"year": 2018, "label": "TESS launch", "color": "#999"},
]


def build_method_colors(methods: list) -> dict:
    """Assign a consistent color from the Vivid palette to each method."""
    return {m: VIVID[i % len(VIVID)] for i, m in enumerate(sorted(methods))}


def _add_mission_lines(fig: go.Figure, y_max: float) -> go.Figure:
    """Overlay vertical lines for Kepler/K2/TESS on a time-axis figure."""
    for event in MISSION_EVENTS:
        fig.add_shape(
            type="line",
            x0=event["year"],
            x1=event["year"],
            y0=0,
            y1=y_max,
            line=dict(color=event["color"], width=1.5, dash="dot"),
            layer="above",
        )
        fig.add_annotation(
            x=event["year"],
            y=y_max * 0.97,
            text=event["label"],
            showarrow=False,
            textangle=-90,
            font=dict(size=10, color=event["color"]),
            xanchor="right",
        )
    return fig


def fig_cumulative(df_cumulative: pd.DataFrame, method_colors: dict) -> go.Figure:
    """Multi-line cumulative discoveries by detection method."""
    fig = go.Figure()
    for method in df_cumulative.columns:
        color = method_colors.get(method, "#aaa")
        fig.add_trace(
            go.Scatter(
                x=df_cumulative.index,
                y=df_cumulative[method],
                mode="lines",
                name=method,
                line=dict(color=color, width=2.5),
                hovertemplate=(
                    f"<b>{method}</b><br>Year: %{{x}}<br>"
                    "Cumulative: %{y:,}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        title=dict(text="Cumulative Exoplanet Discoveries by Detection Method", font=dict(size=16)),
        xaxis=dict(title="Year", tickfont=dict(size=13)),
        yaxis=dict(title="Cumulative Planet Count", tickfont=dict(size=13)),
        legend=dict(title="Method", font=dict(size=12)),
        template="plotly_white",
        hovermode="x unified",
        height=480,
    )
    return fig


def fig_annual_bar(df_annual: pd.DataFrame, method_colors: dict) -> go.Figure:
    """Stacked bar of annual discoveries with mission event annotations."""
    fig = go.Figure()
    for method in df_annual.columns:
        color = method_colors.get(method, "#aaa")
        fig.add_trace(
            go.Bar(
                x=df_annual.index,
                y=df_annual[method],
                name=method,
                marker_color=color,
                hovertemplate=(
                    f"<b>{method}</b><br>Year: %{{x}}<br>"
                    "Discoveries: %{y:,}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        barmode="stack",
        title=dict(text="Annual Exoplanet Discoveries by Detection Method", font=dict(size=16)),
        xaxis=dict(title="Year", tickfont=dict(size=13)),
        yaxis=dict(title="Planets Discovered", tickfont=dict(size=13)),
        legend=dict(title="Method", font=dict(size=12)),
        template="plotly_white",
        height=480,
    )
    y_max = df_annual.sum(axis=1).max() * 1.1
    fig = _add_mission_lines(fig, y_max)
    return fig


def fig_method_share(df_share: pd.DataFrame, method_colors: dict) -> go.Figure:
    """Normalized stacked area chart showing method share per year."""
    fig = go.Figure()
    for method in df_share.columns:
        color = method_colors.get(method, "#aaa")
        fig.add_trace(
            go.Scatter(
                x=df_share.index,
                y=df_share[method],
                name=method,
                mode="lines",
                stackgroup="one",
                line=dict(color=color, width=0.5),
                fillcolor=color,
                hovertemplate=(
                    f"<b>{method}</b><br>Year: %{{x}}<br>"
                    "Share: %{y:.1%}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        title=dict(text="Detection Method Share Over Time", font=dict(size=16)),
        xaxis=dict(title="Year", tickfont=dict(size=13)),
        yaxis=dict(
            title="Fraction of Annual Discoveries",
            tickformat=".0%",
            tickfont=dict(size=13),
            range=[0, 1],
        ),
        legend=dict(title="Method", font=dict(size=12)),
        template="plotly_white",
        height=480,
    )
    return fig


def fig_top_facilities(df_facilities: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of top 15 discovery facilities."""
    df_plot = df_facilities.sort_values("count", ascending=True)
    fig = go.Figure(
        go.Bar(
            x=df_plot["count"],
            y=df_plot["disc_facility"],
            orientation="h",
            marker_color=VIVID[0],
            hovertemplate="<b>%{y}</b><br>Planets: %{x:,}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="Top 15 Discovery Facilities", font=dict(size=16)),
        xaxis=dict(title="Planet Count", tickfont=dict(size=13)),
        yaxis=dict(title="", tickfont=dict(size=12)),
        template="plotly_white",
        height=520,
        margin=dict(l=200),
    )
    return fig


def fig_orbital_scatter(df_scatter: pd.DataFrame, method_colors: dict) -> go.Figure:
    """Log-log scatter of orbital period vs planet radius, colored by method."""
    fig = go.Figure()
    for method, group in df_scatter.groupby("discoverymethod"):
        color = method_colors.get(method, "#aaa")
        fig.add_trace(
            go.Scatter(
                x=group["pl_orbper"],
                y=group["pl_rade"],
                mode="markers",
                name=method,
                marker=dict(color=color, size=5, opacity=0.6),
                hovertemplate=(
                    f"<b>{method}</b><br>"
                    "Period: %{x:.2f} days<br>"
                    "Radius: %{y:.2f} R<sub>Earth</sub><br>"
                    "%{text}<extra></extra>"
                ),
                text=group["pl_name"],
            )
        )
    fig.update_layout(
        title=dict(text="Orbital Period vs Planet Radius", font=dict(size=16)),
        xaxis=dict(
            title="Orbital Period (days)",
            type="log",
            tickfont=dict(size=13),
        ),
        yaxis=dict(
            title="Planet Radius (Earth Radii)",
            type="log",
            tickfont=dict(size=13),
        ),
        legend=dict(title="Method", font=dict(size=12)),
        template="plotly_white",
        height=500,
    )
    return fig


def fig_pre_post_kepler(df_prepost: pd.DataFrame) -> go.Figure:
    """Grouped bar comparing avg annual transit discoveries across mission eras."""
    era_colors = {
        "Pre-Kepler": VIVID[3],
        "Kepler Era": VIVID[0],
        "TESS Era": VIVID[1],
    }
    colors = [era_colors.get(era, VIVID[2]) for era in df_prepost["mission_era"]]
    fig = go.Figure(
        go.Bar(
            x=df_prepost["mission_era"],
            y=df_prepost["avg_annual_transit"].round(1),
            marker_color=colors,
            text=df_prepost["avg_annual_transit"].round(1),
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Avg/year: %{y:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text="Average Annual Transit Discoveries by Mission Era", font=dict(size=16)),
        xaxis=dict(title="Mission Era", tickfont=dict(size=13)),
        yaxis=dict(title="Avg. Planets Discovered per Year", tickfont=dict(size=13)),
        template="plotly_white",
        showlegend=False,
        height=440,
    )
    return fig
