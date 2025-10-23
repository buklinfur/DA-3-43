# Visualization & Analysis of Categorical Data (DA-1-45 -> DA-2-43 -> DA-3-43)

Python package for **visualizing, encoding, and analyzing** categorical data.  
Provides reusable core functions, full-featured CLI commands, and automatic generation of reports (Markdown, CSV, PNG).

---

DA-3-43/
├─ visualize_categorical/
│ ├─ init.py
│ ├─ analyzer.py
│ ├─ core.py
│ ├─ cli.py
│ └─ exit_codes.py
├─ tests/
│ ├─ test_core.py
│ ├─ test_analyzer.py
├─ pyproject.toml
├─ README.md

---

## Modules

### `core.py`

* `create_synthetic_data(n, column_name, categories, probs, seed)` – generate synthetic categorical data.
* `load_csv(path)` – load CSV into DataFrame.
* `validate_category_column(df, col)` – check column exists and is valid.
* `count_categories(df, col)` – return counts of categories.
* `plot_bar(counts, title, xlabel, ylabel, out_path)` – create bar plot.
* `plot_pie(counts, title, out_path)` – create pie chart.
* `encode_categorical(df, column, method)` – encode column using `"onehot"`, `"ordinal"` or `"label"`.

---

### `analyzer.py`

Performs **complex analysis of categorical datasets** (DA-3-43 stage).  
Supports a full automated pipeline: from encoding and statistics to correlation heatmaps and Markdown reports.

#### Main Functions

* `analyze_dataset(df, out_dir, encode="onehot", include=("images","csv","text"))` – high-level pipeline that:
  - encodes all categorical columns,
  - computes per-column distributions,
  - calculates numeric correlation matrix,
  - computes mutual information between categorical pairs,
  - generates and saves all results (CSV, PNG, Markdown).

* `prepare_dataframe(df, encode)` – encodes all categorical columns.  
* `compute_distributions(df)` – returns a summary for each categorical feature.  
* `compute_correlation_matrix(df)` – computes correlation matrix for numeric features.  
* `compute_mutual_info(df)` – computes mutual information matrix for categorical features.  
* `save_heatmap(corr, out_path)` – saves correlation heatmap to file.  
* `build_markdown_report(results, out_path, include_images=True)` – builds a complete Markdown report with embedded plots and auto-generated insights.

#### Example Generated Report

Categorical analysis report
Generated: 2025-10-23T13:37:50 UTC

1. Distributions summary
feature_0: unique=3, top=blue (35.00%)

feature_1: unique=3, top=medium (39.00%)

feature_2: unique=3, top=mouse (41.00%)

2. Correlation matrix
correlation matrix shape: (3, 3)

CSV: correlation.csv

Heatmap: heatmap.png

3. Mutual information
CSV: mutual_info.csv

4. Conclusions
Most skewed feature: feature_2 (41% dominance)

Strongest mutual info: feature_1 ↔ feature_2 (0.073)

---

### `cli.py`

Command-line interface for running the package.

Now supports **two subcommands**:

#### 1. `visualize`
Visualizes a single categorical column (legacy mode).

| Argument    | Type | Default   | Description                                                    |
| ----------- | ---- | --------- | -------------------------------------------------------------- |
| `--input`   | str  | None      | CSV file path. If missing, generates synthetic data.           |
| `--column`  | str  | "color"   | Column name to analyze.                                        |
| `--n`       | int  | 100       | Number of rows for synthetic data.                             |
| `--out-dir` | str  | "figures" | Output directory for plots.                                    |
| `--seed`    | int  | 42        | Random seed for reproducibility.                               |
| `--encoder` | str  | "none"    | Encoding method: `"none"`, `"onehot"`, `"ordinal"`, `"label"`. |
| `--export`  | flag | False     | Save encoded DataFrame to CSV.                                 |

#### 2. `analyze`
Performs multi-column dataset analysis.

| Argument      | Type | Default              | Description |
| -------------- | ---- | -------------------- | ------------ |
| `--input`      | str  | required             | Path to CSV file. |
| `--out-dir`    | str  | "analysis"           | Directory to save reports and plots. |
| `--encode`     | str  | "onehot"             | Encoding for categorical features. |
| `--include`    | str  | "images,csv,text"    | What to include in report (comma-separated). |

Examples:

```bash
visualize-categorical visualize --n 100 --column mood --out-dir figures
visualize-categorical analyze --input data/my_data.csv --out-dir report --encode onehot
Plots, heatmaps, CSVs, and Markdown reports are saved to the output directory.

exit_codes.py
Code	Meaning
0	Success
1	File not found
2	Invalid input
3	Missing config key
4	Runtime failure
99	Unknown error

Installation
bash
Копировать код
git clone <repo_url>
cd DA-3-43
python -m venv .venv

# Windows PowerShell
.venv\Scripts\activate
# or Linux/macOS
source .venv/bin/activate

pip install .
# or
pip install .[dev]  # for tests
Usage
CLI Examples
Generate synthetic dataset and visualize:

bash
Копировать код
visualize-categorical visualize --n 100 --column color --out-dir figures
Full dataset analysis with Markdown report:

bash
Копировать код
visualize-categorical analyze --input data/my_data.csv --out-dir analysis --encode onehot
Help:

bash
Копировать код
visualize-categorical --help
Python API
python
Копировать код
from visualize_categorical.core import create_synthetic_data, count_categories, plot_bar, encode_categorical

df = create_synthetic_data(n=50, column_name="color")
counts = count_categories(df, "color")
plot_bar(counts, title="Color Distribution", xlabel="Color", ylabel="Count", out_path="bar.png")

df_encoded = encode_categorical(df, "color", method="onehot")
Testing
bash
Копировать код
pytest -v
Includes coverage for:

data creation and validation,

category counting and encoding,

analysis reports (Markdown, heatmap, CSV generation).