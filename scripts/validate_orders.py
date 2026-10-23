
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "olist" / "olist_orders_dataset.csv"
CONTRACT_FILE = ROOT / "contracts" / "orders.yml"

TIMESTAMP_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

LIFECYCLE_PAIRS = [
    (
        "purchase > approval",
        "order_purchase_timestamp",
        "order_approved_at",
    ),
    (
        "approval > carrier handoff",
        "order_approved_at",
        "order_delivered_carrier_date",
    ),
    (
        "carrier handoff > delivery",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
    ),
]


def validate_dataframe(
    df: pd.DataFrame, contract: dict
) -> tuple[list[str], list[str]]:
    errors = []
    warnings = []

    expected_columns = set(contract["columns"])
    actual_columns = set(df.columns)

    missing_columns = expected_columns - actual_columns
    unexpected_columns = actual_columns - expected_columns

    if missing_columns:
        errors.append(f"Missing columns: {sorted(missing_columns)}")

    if unexpected_columns:
        errors.append(f"Unexpected columns: {sorted(unexpected_columns)}")

    for column, rules in contract["columns"].items():
        if column not in df.columns:
            continue

        values = df[column].str.strip()
        blank = values.eq("")

        if not rules.get("nullable", True):
            count = int(blank.sum())
            if count:
                errors.append(f"{column}: {count} blank values")

        if "allowed_values" in rules:
            invalid = ~values.isin(rules["allowed_values"])
            count = int(invalid.sum())
            if count:
                errors.append(
                    f"{column}: {count} values outside allowed list"
                )

    if "order_id" in df.columns:
        duplicates = int(df["order_id"].duplicated(keep=False).sum())
        if duplicates:
            errors.append(
                f"order_id: {duplicates} rows involved in duplicate IDs"
            )

    # Parse timestamps without modifying the original strings.
    parsed = {}
    for column in TIMESTAMP_COLUMNS:
        if column not in df.columns:
            continue

        raw = df[column].str.strip()
        present = raw.ne("")
        converted = pd.to_datetime(raw.where(present), errors="coerce")
        parsed[column] = converted

        invalid = present & converted.isna()
        count = int(invalid.sum())
        if count:
            errors.append(f"{column}: {count} invalid timestamp values")

    # Lifecycle ordering checks. Missing optional timestamps are not
    # automatically treated as ordering violations.
    for label, earlier, later in LIFECYCLE_PAIRS:
        if earlier not in parsed or later not in parsed:
            continue

        both_present = parsed[earlier].notna() & parsed[later].notna()
        violation = both_present & (parsed[earlier] > parsed[later])
        count = int(violation.sum())

        if count:
            warnings.append(f"{label}: {count} timestamp-order violations")

    # Missing delivery dates depend on the order's business status.
    if "order_status" in df.columns:
        status = df["order_status"].str.strip()

        if "order_delivered_customer_date" in parsed:
            missing_delivery = (
                status.eq("delivered")
                & parsed["order_delivered_customer_date"].isna()
            )
            count = int(missing_delivery.sum())
            if count:
                warnings.append(
                    f"Delivered orders missing customer delivery timestamp: "
                    f"{count}"
                )

        if "order_estimated_delivery_date" in parsed:
            missing_estimate = (
                status.eq("delivered")
                & parsed["order_estimated_delivery_date"].isna()
            )
            count = int(missing_estimate.sum())
            if count:
                warnings.append(
                    f"Delivered orders missing estimated delivery timestamp: "
                    f"{count}"
                )

    return errors, warnings


def main() -> int:
    with CONTRACT_FILE.open(encoding="utf-8") as file:
        contract = yaml.safe_load(file)

    df = pd.read_csv(DATA_FILE, dtype=str, keep_default_na=False)
    errors, warnings = validate_dataframe(df, contract)

    expected_columns = set(contract["columns"])
    actual_columns = set(df.columns)

    print(f"Dataset rows: {len(df):,}")
    print(f"Contract columns: {len(expected_columns)}")
    print(f"Actual columns: {len(actual_columns)}")

    print("\nWARNINGS")
    if warnings:
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("None")

    print("\nERRORS")
    if errors:
        for error in errors:
            print(f"- {error}")
        print("\nCONTRACT VALIDATION: FAILED")
        return 1

    print("\nCONTRACT VALIDATION: PASSED")
    print("Structural, required-value, status, key and timestamp-format checks passed.")
    print("Review warnings before approving data for publication.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
