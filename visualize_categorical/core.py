from __future__ import annotations
from typing import Optional, Sequence
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder


def ensure_dir(path: str | Path) -> Path:
    """Creates a directory if it does not exist and returns Path object."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def create_synthetic_data(n: int = 100,
                          column_name: str = "color",
                          categories: Sequence[str] = ("red", "blue", "yellow"),
                          probs: Optional[Sequence[float]] = None,
                          seed: Optional[int] = None) -> pd.DataFrame:
    """Creates DataFrame with categorial column and synthetic data. Ensures each category appears at least once when possible."""
    if probs is None:
        probs = [1 / len(categories)] * len(categories)
    if len(probs) != len(categories):
        raise ValueError("probs has to be the same size as categories")
    rng = np.random.default_rng(seed)

    if n >= len(categories):
        # ensure each category appears at least once
        base = list(categories)
        remaining = n - len(base)
        if remaining > 0:
            choices = rng.choice(categories, size=remaining, p=probs)
            vals = np.array(base + choices.tolist())
            rng.shuffle(vals)
        else:
            vals = np.array(base)
    else:
        # n < number of categories, just sample without guarantee
        vals = rng.choice(categories, size=n, p=probs)

    return pd.DataFrame({column_name: vals})



def load_csv(path: str | Path) -> pd.DataFrame:
    """Loads CSV from path into a DataFrame, raises FileNotFoundError if missing."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File {p} not found.")
    return pd.read_csv(p)


def validate_category_column(df: pd.DataFrame, column: str) -> None:
    """Checks that the DataFrame contains the column and it is not empty."""
    if column not in df.columns:
        raise ValueError(f"Колонка '{column}' отсутствует в DataFrame")
    if df[column].dropna().shape[0] == 0:
        raise ValueError(f"Колонка '{column}' пустая или состоит только из NaN")


def count_categories(df: pd.DataFrame, column: str) -> pd.Series:
    """Counts occurrences of each category in a column, returns a Series."""
    validate_category_column(df, column)
    return df[column].value_counts(dropna=False)


def plot_bar(counts: pd.Series, title: str, xlabel: str,
             ylabel: str, out_path: str | Path, figsize=(6, 4),
             dpi: int = 150, rotate: int = 0) -> None:
    """Creates and saves a bar plot from a Series of counts, with labels and optional rotation."""
    ensure_dir(Path(out_path).parent)
    ax = counts.plot(kind="bar", rot=rotate)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=dpi)
    plt.close()


def plot_pie(counts: pd.Series, title: str, out_path: str | Path,
             figsize=(6, 6), dpi: int = 150, autopct: str = "%1.1f%%") -> None:
    """Creates and saves a pie chart from a Series of counts, showing percentages."""
    ensure_dir(Path(out_path).parent)
    fig, ax = plt.subplots(figsize=figsize)
    counts.plot(kind="pie", autopct=autopct, startangle=90, ax=ax)
    ax.set_ylabel("")
    ax.set_title(title)
    ax.axis("equal")
    plt.tight_layout()
    plt.savefig(out_path, dpi=dpi)
    plt.close()


def encode_categorical(df: pd.DataFrame, column: str, method: str = "onehot") -> pd.DataFrame:
    """Encodes a categorical column using 'onehot', 'ordinal', or 'label' method."""
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")

    if method == "onehot":
        df_encoded = pd.get_dummies(df, columns=[column], prefix=column)
    elif method == "ordinal":
        encoder = OrdinalEncoder()
        df_copy = df.copy()
        df_copy[column] = encoder.fit_transform(df_copy[[column]])
        df_encoded = df_copy
    elif method == "label":
        encoder = LabelEncoder()
        df_copy = df.copy()
        df_copy[column] = encoder.fit_transform(df_copy[column])
        df_encoded = df_copy
    else:
        raise ValueError(f"Unknown encoding method: {method}")

    return df_encoded

