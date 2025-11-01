#!/usr/bin/env python
"""Simple Excel import helper.

Reads an Excel file (default: `Volcano Data.xlsx` in the repo), prints a small preview
and writes the full table to `data/output.csv`.

Usage (PowerShell):
  python import_excel.py -i "Volcano Data.xlsx" -o data/output.csv --preview 10
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

try:
    import pandas as pd
except Exception as e:  # pragma: no cover - user missing deps
    print("pandas is required. Install with: python -m pip install -r requirements.txt")
    raise


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Import an Excel file and export to CSV/JSON")
    p.add_argument("-i", "--input", default=None, help="Path to the Excel file")
    p.add_argument("-s", "--sheet", default=0, help="Sheet name or index (default: first sheet)")
    p.add_argument("-o", "--output", default="data/output.csv", help="Output CSV path")
    p.add_argument("--to-json", action="store_true", help="Also write JSON alongside CSV")
    p.add_argument("--preview", type=int, default=10, help="Number of preview rows to print")

    args = p.parse_args(argv)

    repo_root = Path(__file__).parent

    if args.input:
        input_path = Path(args.input)
    else:
        input_path = repo_root / "Volcano Data.xlsx"

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 2

    print(f"Reading: {input_path}")
    try:
        # Let pandas infer engine; openpyxl is used for .xlsx
        df = pd.read_excel(input_path, sheet_name=args.sheet)
    except Exception as exc:
        print("Failed to read Excel file:", exc)
        return 3

    # If a dict of sheets is returned, pick the first
    if isinstance(df, dict):
        # if user passed a sheet name, pandas returns DataFrame; otherwise it's a dict
        # pick the first sheet
        sheet_names = list(df.keys())
        if not sheet_names:
            print("No sheets found in workbook")
            return 4
        print(f"Multiple sheets found; using first: {sheet_names[0]}")
        df = df[sheet_names[0]]

    print("\n--- Preview (first %d rows) ---" % args.preview)
    with pd.option_context("display.max_rows", args.preview, "display.max_columns", 20):
        print(df.head(args.preview).to_string(index=False))

    out_path = Path(args.output)
    out_dir = out_path.parent
    if not out_dir.exists():
        os.makedirs(out_dir, exist_ok=True)

    try:
        df.to_csv(out_path, index=False)
        print(f"\nWrote CSV to: {out_path}")
    except Exception as exc:
        print("Failed to write CSV:", exc)
        return 5

    if args.to_json:
        json_path = out_path.with_suffix(".json")
        try:
            df.to_json(json_path, orient="records", force_ascii=False)
            print(f"Wrote JSON to: {json_path}")
        except Exception as exc:
            print("Failed to write JSON:", exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
