from pathlib import Path

import pandas as pd


DATA_DIR = Path("data/olist")


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def duplicate_key_count(df: pd.DataFrame, keys: list[str]) -> int:
    return int(df.duplicated(subset=keys, keep=False).sum())


def orphan_count(
    child: pd.DataFrame,
    child_key: str,
    parent: pd.DataFrame,
    parent_key: str,
) -> int:
    valid_parent_keys = set(parent[parent_key].dropna())
    values = child[child_key]
    return int((values.notna() & ~values.isin(valid_parent_keys)).sum())


def main() -> None:
    customers = load("olist_customers_dataset.csv")
    orders = load("olist_orders_dataset.csv")
    items = load("olist_order_items_dataset.csv")
    payments = load("olist_order_payments_dataset.csv")
    reviews = load("olist_order_reviews_dataset.csv")
    products = load("olist_products_dataset.csv")
    sellers = load("olist_sellers_dataset.csv")

    print("PRIMARY-KEY CANDIDATES")
    checks = [
        ("customers.customer_id", customers, ["customer_id"]),
        ("customers.customer_unique_id", customers, ["customer_unique_id"]),
        ("orders.order_id", orders, ["order_id"]),
        ("items (order_id, order_item_id)", items, ["order_id", "order_item_id"]),
        ("products.product_id", products, ["product_id"]),
        ("sellers.seller_id", sellers, ["seller_id"]),
        ("payments (order_id, payment_sequential)", payments,
         ["order_id", "payment_sequential"]),
        ("reviews.review_id", reviews, ["review_id"]),
    ]

    for label, df, keys in checks:
        duplicates = duplicate_key_count(df, keys)
        print(f"{label}: {duplicates:,} rows involved in duplicate keys")

    print("\nFOREIGN-KEY ORPHANS")
    relationships = [
        ("orders.customer_id -> customers.customer_id",
         orders, "customer_id", customers, "customer_id"),
        ("items.order_id -> orders.order_id",
         items, "order_id", orders, "order_id"),
        ("items.product_id -> products.product_id",
         items, "product_id", products, "product_id"),
        ("items.seller_id -> sellers.seller_id",
         items, "seller_id", sellers, "seller_id"),
        ("payments.order_id -> orders.order_id",
         payments, "order_id", orders, "order_id"),
        ("reviews.order_id -> orders.order_id",
         reviews, "order_id", orders, "order_id"),
    ]

    for label, child, child_key, parent, parent_key in relationships:
        print(
            f"{label}: "
            f"{orphan_count(child, child_key, parent, parent_key):,} orphan rows"
        )

    print("\nPRODUCT DESCRIPTION NULL PATTERN")
    description_columns = [
        "product_category_name",
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
    ]
    all_four_missing = int(products[description_columns].isna().all(axis=1).sum())
    any_missing = int(products[description_columns].isna().any(axis=1).sum())
    print(f"Rows missing any of these fields: {any_missing:,}")
    print(f"Rows missing all four fields: {all_four_missing:,}")


if __name__ == "__main__":
    main()
