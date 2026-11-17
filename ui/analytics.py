"""
Data formatting and chart generation utilities for Streamlit dashboard.
"""
import pandas as pd

def prepare_chart_dataframe(df: pd.DataFrame) -> pd.DataFrame | None:
    """Prepares clean DataFrame containing views and likes for visualization."""
    if "metrics_likes" not in df.columns:
        return None

    cols = ["id", "metrics_likes"]
    if "metrics_views" in df.columns:
        cols.append("metrics_views")

    chart_df = df[cols].copy()
    chart_df["id"] = chart_df["id"].astype(str)
    return chart_df.set_index("id")

def get_metric_summary(df: pd.DataFrame) -> dict[str, int]:
    """Calculate total and average engagement stats from scraped DataFrame."""
    summary = {
        "total_likes": int(df["metrics_likes"].sum()) if "metrics_likes" in df.columns else 0,
        "total_comments": int(df["metrics_comments"].sum()) if "metrics_comments" in df.columns else 0,
        "total_views": int(df["metrics_views"].sum()) if "metrics_views" in df.columns else 0,
    }
    return summary
