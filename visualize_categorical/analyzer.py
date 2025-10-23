# visualize_categorical/analyzer.py
from __future__ import annotations
from typing import Iterable, Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import os

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import mutual_info_score

from .core import encode_categorical

# -------------------------
# Utility / compute blocks
# -------------------------

def prepare_dataframe(df: pd.DataFrame, encode: Optional[str] = "onehot") -> pd.DataFrame:
    """Return dataframe prepared for analysis (optionally encoded)."""
    if encode and encode != "none":
        return encode_categorical(df.copy(), column=None, method=encode) if False else _encode_all_columns(df.copy(), method=encode)
    return df.copy()


def _encode_all_columns(df: pd.DataFrame, method: str = "onehot") -> pd.DataFrame:
    """Encode all object / categorical columns using method. onehot expands columns."""
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if method == "onehot":
        return pd.get_dummies(df, columns=cat_cols, prefix=cat_cols)
    elif method == "ordinal":
        enc_df = df.copy()
        for c in cat_cols:
            enc = pd.factorize(enc_df[c])[0]
            enc_df[c] = enc
        return enc_df
    elif method == "label":
        enc_df = df.copy()
        for c in cat_cols:
            enc_df[c] = pd.factorize(enc_df[c])[0]
        return enc_df
    else:
        raise ValueError(f"Unknown encode method: {method}")


def compute_distributions(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute per-column counts and rare categories summary."""
    res = {}
    for c in df.select_dtypes(include=["object", "category"]).columns:
        vc = df[c].value_counts(dropna=False)
        res[c] = {
            "counts": vc,
            "n_unique": int(vc.size),
            "most_freq": vc.idxmax(),
            "most_freq_share": float(vc.max() / len(df))
        }
    return res


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Compute correlation matrix for numeric columns (after one-hot)."""
    numeric = df.select_dtypes(include=[np.number, "bool"]).copy()
    # Convert bool → int if needed
    for c in numeric.columns:
        if numeric[c].dtype == bool:
            numeric[c] = numeric[c].astype(int)
    return numeric.corr()


def compute_mutual_info(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Compute pairwise mutual information for categorical columns (slow but descriptive)."""
    if columns is None:
        columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
    n = len(columns)
    mi = pd.DataFrame(np.zeros((n, n)), index=columns, columns=columns)
    for i, a in enumerate(columns):
        for j, b in enumerate(columns[i + 1 :], start=i + 1):
            mi_val = mutual_info_score(df[a], df[b])
            mi.loc[a, b] = mi_val
            mi.loc[b, a] = mi_val
    return mi

# -------------------------
# Output / visualization
# -------------------------

def save_heatmap(corr: pd.DataFrame, out_path: Path, figsize=(10, 8)) -> Path:
    """Save heatmap image and return path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if corr.empty:
        plt.figure(figsize=(4, 3))
        plt.text(0.5, 0.5, "No numeric correlation available", ha="center", va="center")
        plt.axis("off")
        plt.savefig(out_path, dpi=150)
        plt.close()
        return out_path

    plt.figure(figsize=figsize)
    sns.heatmap(corr, cmap="vlag", center=0, xticklabels=True, yticklabels=True)
    plt.title("Correlation heatmap")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def save_csv(df: pd.DataFrame, out_path: Path) -> Path:
    """Save DataFrame to CSV and return path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=True)
    return out_path


def build_markdown_report(results: Dict[str, Any], out_path: Path, include_images: bool = True) -> Path:
    """Create a markdown report with sections and (optionally) embed images."""
    lines: List[str] = []
    lines.append(f"# Categorical analysis report")
    lines.append(f"Generated: {datetime.utcnow().isoformat()} UTC")
    lines.append("")

    # distributions summary
    dist = results.get("distributions", {})
    lines.append("## 1. Distributions summary")
    for col, info in dist.items():
        lines.append(f"- **{col}**: unique={info['n_unique']}, top={info['most_freq']} ({info['most_freq_share']:.2%})")
    lines.append("")

    # correlation
    corr_path = results.get("corr_csv")
    corr_shape = results.get("corr_shape")
    lines.append("## 2. Correlation matrix")
    if corr_shape:
        lines.append(f"- correlation matrix shape: {corr_shape}")
    if corr_path:
        lines.append(f"- CSV: `{Path(corr_path).name}`")
    # embed image
    heatmap_path = results.get("heatmap")
    if include_images and heatmap_path:
        rel = Path(heatmap_path).name
        lines.append("")
        lines.append(f"![heatmap]({rel})")
    lines.append("")

    # mutual info
    mi_path = results.get("mi_csv")
    if mi_path:
        lines.append("## 3. Mutual information (categorical pairs)")
        lines.append(f"- CSV: `{Path(mi_path).name}`")
        lines.append("")

    # Conclusions: generate multiple observations
    lines.append("## 4. Conclusions")
    concl = _generate_conclusions(results)
    for c in concl:
        lines.append(f"- {c}")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def _generate_conclusions(results: Dict[str, Any]) -> List[str]:
    """Heuristic conclusions extracted from results dict."""
    concl: List[str] = []
    # correlation extremes
    corr_df: Optional[pd.DataFrame] = results.get("corr")
    if corr_df is not None and not corr_df.empty and corr_df.dropna(how="all").shape[0] > 1:
        stacked = corr_df.where(np.triu(np.ones(corr_df.shape), k=1).astype(bool)).stack()
        if not stacked.empty:
            max_pair = stacked.idxmax()
            max_val = stacked.max()
            min_pair = stacked.idxmin()
            min_val = stacked.min()
            concl.append(f"Max positive correlation {max_val:.2f} between {max_pair[0]} and {max_pair[1]}.")
            concl.append(f"Max negative correlation {min_val:.2f} between {min_pair[0]} and {min_pair[1]}.")
        # average magnitude
        avg_abs = stacked.abs().mean() if not stacked.empty else 0.0
        if avg_abs < 0.2:
            concl.append("Overall correlations are weak (avg |r| < 0.2), features mostly independent.")
        else:
            concl.append(f"Average absolute pairwise correlation is {avg_abs:.2f}, some dependencies exist.")
    # diversity observations
    dist = results.get("distributions", {})
    if dist:
        most_skew = max(dist.items(), key=lambda x: x[1]["most_freq_share"])
        concl.append(f"Most skewed category: {most_skew[0]}, top value share = {most_skew[1]['most_freq_share']:.2%}.")
        many_unique = [k for k, v in dist.items() if v["n_unique"] > 10]
        if many_unique:
            concl.append(f"High-cardinality features: {', '.join(many_unique)}.")
    # mutual info observations
    mi = results.get("mi")
    if isinstance(mi, pd.DataFrame) and not mi.empty:
        top_mi = mi.stack().idxmax()
        top_val = mi.stack().max()
        concl.append(f"Top mutual information {top_val:.3f} between {top_mi[0]} and {top_mi[1]}.")
    # recommendation
    concl.append("Consider dimensionality reduction or feature selection if many one-hot columns.")
    return concl

# -------------------------
# High-level pipeline
# -------------------------

def analyze_dataset(df: pd.DataFrame,
                    out_dir: str | Path = "analysis",
                    encode: Optional[str] = "onehot",
                    include: Iterable[str] = ("images", "csv", "text")) -> Dict[str, Any]:
    """Run full analysis pipeline and save outputs according to include list."""
    out_dir = Path(out_dir)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    job_dir = out_dir / f"analysis_{ts}"
    job_dir.mkdir(parents=True, exist_ok=True)

    include_set = set(include)
    results: Dict[str, Any] = {}

    # prepare
    df_prepared = prepare_dataframe(df, encode=encode)
    results["prepared_shape"] = df_prepared.shape

    # distributions (before encode)
    results["distributions"] = compute_distributions(df)

    # correlation
    corr = compute_correlation_matrix(df_prepared)
    corr_clean = corr.dropna(axis=0, how="all").dropna(axis=1, how="all")

    results["corr"] = corr
    results["corr_shape"] = corr.shape

    if "csv" in include_set:
        path = save_csv(corr, job_dir / "correlation.csv")
        results["corr_csv"] = path

    # heatmap 
    if "images" in include_set:
        if corr_clean.empty:
            results["heatmap"] = None
        else:
            heat_path = job_dir / "heatmap.png"
            results["heatmap"] = save_heatmap(corr_clean, heat_path)


    # mutual info (on original categorical columns)
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        mi = compute_mutual_info(df, columns=cat_cols)
        results["mi"] = mi
        if "csv" in include_set:
            path = save_csv(mi, job_dir / "mutual_info.csv")
            results["mi_csv"] = path

    # markdown report
    report_path = job_dir / "report.md"
    include_images = "images" in include_set
    build_markdown_report(results, report_path, include_images=include_images)
    results["report"] = report_path

    return results
