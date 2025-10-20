import pandas as pd
import pytest
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder

from visualize_categorical.core import (
    create_synthetic_data,
    validate_category_column,
    count_categories,
    encode_categorical,
)


def test_create_synthetic_data_shape():
    df = create_synthetic_data(n=50, column_name="color", seed=42)
    assert df.shape == (50, 1)
    assert "color" in df.columns


def test_validate_and_count(tmp_path):
    df = pd.DataFrame({"color": ["red", "blue", "red"]})
    validate_category_column(df, "color")
    counts = count_categories(df, "color")
    assert counts["red"] == 2
    assert counts["blue"] == 1


def test_validate_missing_column():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError):
        validate_category_column(df, "color")


def test_encode_onehot():
    df = pd.DataFrame({"color": ["red", "blue", "red"]})
    df_encoded = encode_categorical(df, "color", method="onehot")
    assert "color_red" in df_encoded.columns
    assert "color_blue" in df_encoded.columns
    # original column should be removed
    assert "color" not in df_encoded.columns
    # values are 0/1
    assert set(df_encoded["color_red"].unique()) <= {0, 1}
    # check number of new columns matches number of unique categories 
    n_unique = df["color"].nunique()
    n_encoded_cols = sum(col.startswith("color_") for col in df_encoded.columns)
    assert n_encoded_cols == n_unique


def test_encode_ordinal():
    df = pd.DataFrame({"color": ["red", "blue", "green"]})
    df_encoded = encode_categorical(df, "color", method="ordinal")
    assert df_encoded["color"].dtype.kind in "if"  # numeric
    # values are consecutive integers starting from 0
    unique_vals = sorted(df_encoded["color"].unique())
    assert unique_vals == list(range(len(unique_vals)))


def test_encode_label():
    df = pd.DataFrame({"color": ["red", "blue", "green"]})
    df_encoded = encode_categorical(df, "color", method="label")
    assert df_encoded["color"].dtype.kind in "i"  # integer
    unique_vals = sorted(df_encoded["color"].unique())
    assert unique_vals == list(range(len(unique_vals)))


def test_encode_invalid_method():
    df = pd.DataFrame({"color": ["red", "blue"]})
    with pytest.raises(ValueError):
        encode_categorical(df, "color", method="unknown")


def test_encode_missing_column():
    df = pd.DataFrame({"a": [1, 2]})
    with pytest.raises(KeyError):
        encode_categorical(df, "color", method="onehot")
