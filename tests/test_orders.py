import pandas as pd
import yaml

from scripts.validate_orders import validate_dataframe


def load_contract():
    with open("contracts/orders.yml", encoding="utf-8") as file:
        return yaml.safe_load(file)


def valid_order():
    return {
        "order_id": "order-001",
        "customer_id": "customer-001",
        "order_status": "delivered",
        "order_purchase_timestamp": "2018-01-01 10:00:00",
        "order_approved_at": "2018-01-01 10:10:00",
        "order_delivered_carrier_date": "2018-01-02 10:00:00",
        "order_delivered_customer_date": "2018-01-03 10:00:00",
        "order_estimated_delivery_date": "2018-01-05 10:00:00",
    }


def test_valid_order_passes():
    errors, warnings = validate_dataframe(
        pd.DataFrame([valid_order()]), load_contract()
    )
    assert errors == []
    assert warnings == []


def test_duplicate_order_id_is_detected():
    order = valid_order()
    second_order = {**order, "customer_id": "customer-002"}
    errors, _ = validate_dataframe(
        pd.DataFrame([order, second_order]), load_contract()
    )
    assert any("duplicate IDs" in error for error in errors)


def test_invalid_order_status_is_detected():
    order = valid_order()
    order["order_status"] = "teleported"
    errors, _ = validate_dataframe(
        pd.DataFrame([order]), load_contract()
    )
    assert any("outside allowed list" in error for error in errors)