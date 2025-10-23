import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd

from .core import (
    create_synthetic_data,
    load_csv,
    count_categories,
    plot_bar,
    plot_pie,
    encode_categorical,
)
from .analyzer import analyze_dataset
from visualize_categorical import exit_codes


def _ensure_out_dir(p: str | Path) -> Path:
    p = Path(p)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _parse_include(s: str) -> List[str]:
    return [x.strip() for x in s.split(",") if x.strip()]


def run_visualize(
    input_path: str | None,
    column: str,
    out_dir: str,
    n: int = 100,
    seed: int | None = 42,
    encoder: str = "none",
    export: bool = False,
) -> dict:
    """Run visualization workflow (one column)."""
    out_dir = _ensure_out_dir(out_dir)

    if input_path:
        df = load_csv(input_path)
    else:
        df = create_synthetic_data(n=n, column_name=column, seed=seed)

    if encoder != "none":
        df = encode_categorical(df, column, method=encoder)
        print(f"[INFO] Column '{column}' encoded using '{encoder}'")

    # counts for plotting
    if encoder == "onehot":
        # sum each one-hot column that starts with original column name + separator
        mask = df.columns.str.startswith(f"{column}_")
        counts = df.loc[:, mask].sum()
        # keep index names as strings for plotting
        counts.index = [str(i) for i in counts.index]
    else:
        counts = count_categories(df, column)

    bar_path = out_dir / f"bar_{column}.png"
    pie_path = out_dir / f"pie_{column}.png"

    plot_bar(counts, title=f"Distribution by {column}", xlabel=column, ylabel="Amount", out_path=bar_path)
    plot_pie(counts, title=f"Fractions by {column}", out_path=pie_path)

    result = {"bar": str(bar_path), "pie": str(pie_path)}

    if export:
        csv_path = out_dir / f"encoded_{column}.csv"
        df.to_csv(csv_path, index=False)
        result["csv"] = str(csv_path)
        print(f"[INFO] Encoded data saved to: {csv_path}")

    return result


def run_analyze(
    input_path: str,
    out_dir: str = "analysis",
    encode: str = "onehot",
    include: str = "images,csv,text",
) -> dict:
    """Run full dataset categorical analysis and save outputs."""
    # load data
    df = load_csv(input_path)
    include_list = _parse_include(include)
    res = analyze_dataset(df, out_dir=out_dir, encode=None if encode == "none" else encode, include=include_list)
    print(f"[INFO] Analysis complete. Report saved to: {res.get('report')}")
    return res


def run_legacy(args) -> dict:
    """Legacy behavior: old single-run CLI (keeps compatibility)."""
    return run_visualize(
        input_path=args.input,
        column=args.column,
        out_dir=args.out_dir,
        n=args.n,
        seed=args.seed,
        encoder=args.encoder,
        export=args.export,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="visualize-categorical", description="Visualize and analyze categorical data")
    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # visualize subcommand (old functionality)
    vis = subparsers.add_parser("visualize", help="visualize single categorical column (same as legacy mode)")
    vis.add_argument("--input", type=str, default=None, help="CSV file (optional). If not specified, generates synthetic data")
    vis.add_argument("--column", type=str, default="color", help="Name of the categorical column")
    vis.add_argument("--out-dir", type=str, default="figures", help="Output directory for results")
    vis.add_argument("--n", type=int, default=100, help="Size of synthetic dataset (if generated)")
    vis.add_argument("--seed", type=int, default=42, help="Random seed for generation")
    vis.add_argument("--encoder", type=str, choices=["none", "onehot", "ordinal", "label"], default="none", help="Encoding method for categorical column")
    vis.add_argument("--export", action="store_true", help="Save encoded DataFrame to CSV")

    # analyze subcommand (new)
    an = subparsers.add_parser("analyze", help="run full categorical analysis (multiple features)")
    an.add_argument("--input", type=str, required=True, help="Path to input CSV file for analysis")
    an.add_argument("--out-dir", type=str, default="analysis", help="Directory to save analysis outputs")
    an.add_argument("--encode", type=str, choices=["onehot", "ordinal", "label", "none"], default="onehot", help="Encode categorical columns before analysis")
    an.add_argument("--include", type=str, default="images,csv,text", help="Comma-separated parts to include in report: images,csv,text")

    # legacy/simple flat args (kept for backward compatibility when no subcommand used)
    parser.add_argument("--input", type=str, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--column", type=str, default="color", help=argparse.SUPPRESS)
    parser.add_argument("--out-dir", type=str, default="figures", help=argparse.SUPPRESS)
    parser.add_argument("--n", type=int, default=100, help=argparse.SUPPRESS)
    parser.add_argument("--seed", type=int, default=42, help=argparse.SUPPRESS)
    parser.add_argument("--encoder", type=str, choices=["none", "onehot", "ordinal", "label"], default="none", help=argparse.SUPPRESS)
    parser.add_argument("--export", action="store_true", help=argparse.SUPPRESS)

    return parser


def main() -> int:
    """Main entrypoint for CLI script."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "visualize":
            run_visualize(
                input_path=args.input,
                column=args.column,
                out_dir=args.out_dir,
                n=args.n,
                seed=args.seed,
                encoder=args.encoder,
                export=args.export,
            )
        elif args.command == "analyze":
            run_analyze(
                input_path=args.input,
                out_dir=args.out_dir,
                encode=args.encode,
                include=args.include,
            )
        else:
            # no subcommand: keep legacy behaviour (flat args)
            run_legacy(args)

        return exit_codes.SUCCESS

    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}", file=sys.stderr)
        return exit_codes.ERR_FILE_NOT_FOUND

    except ValueError as e:
        print(f"[ERROR] Invalid input: {e}", file=sys.stderr)
        return exit_codes.ERR_INVALID_INPUT

    except KeyError as e:
        print(f"[ERROR] Missing config key: {e}", file=sys.stderr)
        return exit_codes.ERR_CONFIG

    except RuntimeError as e:
        print(f"[ERROR] Runtime failure: {e}", file=sys.stderr)
        return exit_codes.ERR_RUNTIME

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        return exit_codes.ERR_UNKNOWN


if __name__ == "__main__":
    sys.exit(main())
