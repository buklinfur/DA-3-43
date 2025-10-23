# Visualization & Analysis of Categorical Data (DA-1-45 → DA-2-43 → DA-3-43)

Python package for **visualizing, encoding, and analyzing** categorical data.  
Provides reusable core functions, full-featured CLI commands, and automatic generation of reports (Markdown, CSV, PNG).

---

## Project Structure

```

DA-3-43/
├─ visualize_categorical/
│  ├─ **init**.py
│  ├─ core.py
│  ├─ analyzer.py
│  ├─ cli.py
│  └─ exit_codes.py
├─ tests/
│  ├─ test_core.py
│  ├─ test_analyzer.py
├─ pyproject.toml
├─ README.md
├─ requirements.txt

```

---

## Modules Overview

### `core.py`

Base utilities for data creation, validation, visualization, and encoding.

* `create_synthetic_data(n, column_name, categories, probs, seed)` – generate synthetic categorical dataset (ensures all categories appear).
* `load_csv(path)` – load CSV into a `pandas.DataFrame`.
* `validate_category_column(df, col)` – verify the existence and non-emptiness of a column.
* `count_categories(df, col)` – return counts of categories as a Series.
* `plot_bar(counts, title, xlabel, ylabel, out_path)` – save bar plot.
* `plot_pie(counts, title, out_path)` – save pie chart.
* `encode_categorical(df, column, method)` – encode one categorical column using `"onehot"`, `"ordinal"`, or `"label"`.

---

### `analyzer.py`

Performs **complex analysis of categorical datasets** (DA-3-43 stage).  
Supports full pipeline generation: from encoded data to correlation heatmaps and Markdown reports.

#### Main Functions

* `analyze_dataset(df, out_dir, encode="onehot", include=("images","csv","text"))` – high-level pipeline that:
  - encodes all categorical columns,
  - computes per-column distributions,
  - calculates numeric correlation matrix,
  - computes mutual information between categorical pairs,
  - saves all results (CSV, PNG, Markdown).

* `prepare_dataframe(df, encode)` – encodes all categorical columns.
* `compute_distributions(df)` – summary for each categorical feature.
* `compute_correlation_matrix(df)` – correlation matrix for numeric features.
* `compute_mutual_info(df)` – mutual information matrix between categorical features.
* `save_heatmap(corr, out_path)` – saves correlation heatmap.
* `build_markdown_report(results, out_path, include_images=True)` – creates a complete Markdown report with embedded figures and automatically generated conclusions.

#### Example Generated Report

```

# Categorical analysis report

Generated: 2025-10-23T13:37:50+00:00

## 1. Distributions summary

* feature_0: unique=3, top=blue (35.00%)
* feature_1: unique=3, top=medium (39.00%)
* feature_2: unique=3, top=mouse (41.00%)

## 2. Correlation matrix

* correlation matrix shape: (0, 0)
* CSV: correlation.csv
  ![heatmap](heatmap.png)

## 3. Mutual information (categorical pairs)

* CSV: mutual_info.csv

## 4. Conclusions

* Most skewed category: feature_2, top value share = 41.00%.
* Top mutual information 0.073 between feature_1 and feature_2.
* Consider dimensionality reduction or feature selection if many one-hot columns.

````

---

### `cli.py`

Command-line interface exposing two main entry points:

| Command | Description |
|----------|-------------|
| `visualize-categorical visualize` | Create plots and optionally encode data. |
| `visualize-categorical analyze` | Perform full analysis and generate Markdown report. |

#### Common Arguments

| Argument    | Type | Default   | Description                                                    |
| ----------- | ---- | --------- | -------------------------------------------------------------- |
| `--input`   | str  | None      | CSV file path. If missing, generates synthetic data.           |
| `--column`  | str  | "color"   | Column name for visualization.                                |
| `--n`       | int  | 100       | Number of rows for synthetic data.                             |
| `--out-dir` | str  | "figures" | Output directory.                                              |
| `--seed`    | int  | 42        | Random seed for reproducibility.                               |
| `--encoder` | str  | "none"    | Encoding method: `"none"`, `"onehot"`, `"ordinal"`, `"label"`. |
| `--export`  | flag | False     | Save encoded DataFrame to CSV.                                 |
| `--help`    | -    | -         | Show help message.                                             |

#### Additional `analyze` Parameters

| Argument | Description |
|-----------|-------------|
| `--include` | Comma-separated list of outputs to generate (`images`, `csv`, `text`). |
| `--out-dir` | Output folder for full analysis job (creates timestamped subfolder). |

---

### `exit_codes.py`

| Code | Meaning            |
| ---- | ------------------ |
| 0    | Success            |
| 1    | File not found     |
| 2    | Invalid input      |
| 3    | Missing config key |
| 4    | Runtime failure    |
| 99   | Unknown error      |

---

## Installation

```bash
git clone <repo_url>
cd DA-3-43
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
# or
source .venv/bin/activate  # Linux / macOS

pip install .
# for tests
pip install .[dev]
````

---

## Usage Examples

### 1. Visualization (bar & pie plots)

```bash
visualize-categorical visualize --n 100 --column mood --out-dir figures --seed 42
```

### 2. Encoding and Export

```bash
visualize-categorical visualize --n 50 --column color --encoder onehot --export --out-dir encoded
```

### 3. Full Analysis & Report Generation

```bash
visualize-categorical analyze --n 100 --out-dir report
```

Creates a subfolder like:

```
report/
└─ analysis_20251023_133750/
   ├─ correlation.csv
   ├─ mutual_info.csv
   ├─ heatmap.png
   └─ report.md
```

---

## Programmatic Usage (Python)

```python
from visualize_categorical.core import create_synthetic_data
from visualize_categorical.analyzer import analyze_dataset

df = create_synthetic_data(n=100, column_name="color")
results = analyze_dataset(df, out_dir="analysis", encode="onehot")
print(results["report"])  # Path to generated Markdown report
```

---

## Testing

```bash
pytest -v
```

Covers:

* synthetic data creation and validation
* encoding and visualization functions
* analyzer pipeline (report generation, CSV/PNG outputs)