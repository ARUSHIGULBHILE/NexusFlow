
# NexusFlow: Delivery KPI Definition

## 1. KPI name
On-Time Delivery Rate

## 2. Business question
What proportion of eligible delivered orders reached customers on or before their estimated delivery timestamps?

## 3. Source
Olist Brazilian E-Commerce Public Dataset:
olist_orders_dataset.csv

## 4. Eligibility rules
Include an order only when all conditions hold:
- order_status equals "delivered"
- order_purchase_timestamp is present
- order_delivered_customer_date is present
- order_estimated_delivery_date is present

## 5. Calculation
On-time order:
Actual delivery timestamp <= Estimated delivery timestamp

Late order:
Actual delivery timestamp > Estimated delivery timestamp

On-Time Delivery Rate:
(On-time or early eligible orders / Total eligible orders) * 100

## 6. Preliminary baseline
- Eligible orders: 96,470
- On-time or early: 88,644
- Late: 7,826
- On-time delivery rate: 91.89%

These are initial profiling results. They must be independently
reconciled before being approved for publication.

## 7. Data-quality observations
- 8 delivered-status orders have missing customer delivery timestamps.
- 1,359 records have approval timestamps later than carrier handoff.
- 23 records have carrier handoff timestamps later than customer delivery.
- No delivered-status orders have missing purchase timestamps.

Timestamp anomalies must be investigated and reported.
Do not silently delete or exclude records solely because of an
unrelated timestamp anomaly.

## 8. Publication requirements
Every published KPI must identify:
- Numerator and denominator
- Excluded record count and exclusion reasons
- Reporting period
- Data freshness
- Contributing batch identifiers
- Last successful publication

A failed critical batch must not overwrite the last known-good KPI.

## 9. Current status
The baseline is provisional. Independent reconciliation,
database implementation and automated validation are pending.
