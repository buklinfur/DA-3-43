# Visualization of Categorical Data (DA-1-45 -> DA-2-43)

Python package for visualizing and encoding categorical data. Provides reusable functions for counting categories, plotting bar and pie charts, encoding columns, and a CLI for CSV files or synthetic data.

---

## Project Structure

```
DA-2-43/
├─ visualize_categorical/
│  ├─ __init__.py
│  ├─ core.py
│  ├─ cli.py
│  └─ exit_codes.py
├─ tests/
│  ├─ test_core.py
├─ pyproject.toml
├─ README.md
├─ requirements.txt
```

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

### `cli.py`

Command-line interface for running the package.

| Argument    | Type | Default   | Description                                                    |
| ----------- | ---- | --------- | -------------------------------------------------------------- |
| `--input`   | str  | None      | CSV file path. If missing, generates synthetic data.           |
| `--column`  | str  | "color"   | Column name to analyze.                                        |
| `--n`       | int  | 100       | Number of rows for synthetic data.                             |
| `--out-dir` | str  | "figures" | Output directory for plots.                                    |
| `--seed`    | int  | 42        | Random seed for reproducibility.                               |
| `--encoder` | str  | "none"    | Encoding method: `"none"`, `"onehot"`, `"ordinal"`, `"label"`. |
| `--export`  | flag | False     | Save encoded DataFrame to CSV.                                 |
| `--help`    | -    | -         | Show CLI help message.                                         |

Plots and optional CSV are saved to `--out-dir`.

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
cd DA-2-43
python -m venv .venv

# Windows PowerShell
.venv\Scripts\activate
# -- or --
# Linux bash
source venv/bin/activate

pip install .
# -- or --
pip install .[dev] # for tests
```

---

## Usage

### CLI

CSV input:

```bash
visualize-categorical --input data/my_data.csv --column color --out-dir figures
```

Synthetic data:

```bash
visualize-categorical --n 100 --column mood --out-dir figures --seed 42
```

One-hot encoding:

```bash
visualize-categorical --n 50 --column color --out-dir figures-onehot --encoder onehot --export
```

Help:

```bash
visualize-categorical --help
```

### Python

```python
from visualize_categorical.core import create_synthetic_data, count_categories, plot_bar, encode_categorical

df = create_synthetic_data(n=50, column_name="color")
counts = count_categories(df, "color")
plot_bar(counts, title="Color Distribution", xlabel="Color", ylabel="Count", out_path="bar.png")

df_encoded = encode_categorical(df, "color", method="onehot")
```

---

## Testing

```bash
pytest -v
```

* Covers data creation, category counting, validation, and encoding.
