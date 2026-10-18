from pathlib import Path
import json

import pandas as pd

DATA_DIR = Path("data/olist")
REPORT_DIR = Path("reports")


def profile_file(path: Path) -> dict:
    df = pd.read_csv(path)

    columns = {}
    for column in df.columns:
        series = df[column]
        columns[column] = {
            "dtype": str(series.dtype),
            "null_count": int(series.isna().sum()),
            "null_pct": round(float(series.isna().mean() * 100), 2),
            "distinct_values": int(series.nunique(dropna=True)),
        }

    return {
        "file": path.name,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": columns,
    }


def main() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(f"Dataset directory not found: {DATA_DIR}")

    files = sorted(DATA_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "dataset_directory": str(DATA_DIR),
        "file_count": len(files),
        "files": [profile_file(path) for path in files],
    }

    output_path = REPORT_DIR / "dataset_profile.json"
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Profiled {len(files)} CSV files.")
    print(f"Report written to: {output_path}")
    print()

    for item in report["files"]:
        print(
            f"{item['file']}: "
            f"{item['row_count']:,} rows, "
            f"{item['column_count']} columns, "
            f"{item['duplicate_rows']:,} exact duplicate rows"
        )


if __name__ == "__main__":
    main()
