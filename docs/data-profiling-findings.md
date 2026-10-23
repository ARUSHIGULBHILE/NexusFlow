# NexusFlow: Initial Data Profiling Findings

## Scope

Dataset: Olist Brazilian E-Commerce Public Dataset  
Files inspected: 9 CSV files in `data/olist/`

## Inventory

| File | Rows | Columns |
|---|---:|---:|
| olist_customers_dataset.csv | 99,441 | 5 |
| olist_geolocation_dataset.csv | 1,000,163 | 5 |
| olist_order_items_dataset.csv | 112,650 | 7 |
| olist_order_payments_dataset.csv | 103,886 | 5 |
| olist_order_reviews_dataset.csv | 99,224 | 7 |
| olist_orders_dataset.csv | 99,441 | 8 |
| olist_products_dataset.csv | 32,951 | 9 |
| olist_sellers_dataset.csv | 3,095 | 4 |
| product_category_name_translation.csv | 71 | 2 |

## Initial Observations

- The geolocation file contains 261,831 exact duplicate rows.
- The review file contains 1,603 rows involved in repeated `review_id` values,
  covering 789 distinct repeated IDs.
- All 789 repeated review IDs occur across different orders.
- The 1,603 rows involved in repeated review IDs match across all columns
  except `order_id`.
- No repeated review ID group has multiple distinct review scores or
  multiple distinct comment messages.
- The four product descriptive fields
  (`product_category_name`, `product_name_lenght`,
  `product_description_lenght`, `product_photos_qty`)
  are missing together in 610 rows.
- The six tested foreign-key relationships reported zero orphan rows.
- `customer_unique_id` is repeated across customer records and must not
  be treated as the unique row key for the customer table without a
  separate business justification.

## Missing-Value Observations

- Review titles: 87,656 nulls (88.34%).
- Review messages: 58,247 nulls (58.70%).
- Order approval timestamp: 160 nulls (0.16%).
- Carrier handoff timestamp: 1,783 nulls (1.79%).
- Customer delivery timestamp: 2,965 nulls (2.98%).
- Product category and three descriptive fields: 610 nulls each (1.85%).
- Product weight and three physical dimensions: 2 nulls each (0.01%).

## Interpretation and Limitations

These are initial profiling observations, not a final defect classification.
Missing values must be interpreted in context, particularly for optional
review text and orders that were cancelled or never delivered.

Repeated review IDs and geolocation rows require further investigation.
No records have been deleted or silently deduplicated.

The foreign-key checks cover only the six relationships tested so far.
Timestamp validity, delivery KPI eligibility, and additional business
constraints remain to be validated.

## Order Lifecycle Timestamp Anomalies

Validation of the 99,441-row Olist orders dataset identified 1,382 distinct orders with lifecycle timestamp-order anomalies.

- Purchase timestamp later than approval timestamp: 0 orders.
- Approval timestamp later than carrier handoff: 1,359 orders.
- Carrier handoff timestamp later than customer delivery: 23 orders.

The combined check identified 1,382 distinct affected orders, with no overlap between the two observed violation categories.

These anomalies are retained and reported as warnings. They are not automatically corrected, deleted, or excluded from delivery KPI calculations solely because of timestamp ordering. KPI eligibility is determined by the documented business rules.

The current validator reports these lifecycle anomalies separately from contract validation errors. A passing contract validation result therefore does not imply that all source records have a plausible event timeline.