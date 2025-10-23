import pandas as pd
import os
from visualize_categorical.analyzer import analyze_dataset

def test_analyze_creates_outputs(tmp_path):
    df = pd.DataFrame({
        "color": ["red","blue","red","green"],
        "shape": ["circle","square","circle","triangle"],
        "material": ["wood","metal","wood","plastic"]
    })
    res = analyze_dataset(df, out_dir=tmp_path, encode="onehot", include=("images","csv","text"))
    assert os.path.exists(res["report"])
    assert os.path.exists(res["corr_csv"])
    assert os.path.exists(res["mi_csv"])
    assert os.path.exists(res["heatmap"])
    # Check markdown contains heatmap embed
    text = open(res["report"], encoding="utf-8").read()
    assert "## 2. Correlation matrix" in text
    assert "heatmap" in text.lower()  # loose check
