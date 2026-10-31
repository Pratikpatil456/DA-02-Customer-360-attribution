# Customer 360 and Marketing Attribution Platform (DA-02)

This project combines GA4 web and app events, synthetic CRM customers, and ad-spend data into one customer view. It then shows which marketing channels bring revenue. The models are built in dbt on BigQuery, the attribution comparison runs in Python, and the dashboards are built in Tableau.

## Architecture

```
GA4 sample e-commerce (BigQuery public dataset)  +  CRM, identity map and ad spend (dbt seeds from Python)
        |
        v
dbt staging  (clean GA4 events and seeds)
        |
        v
dbt intermediate  (identity resolution, order touchpoints)
        |                         |
        v                         v
dbt marts                 Python attribution (first touch, last touch, linear, time decay)
(fct_sessions, fct_orders,        |
 dim_customer, customer_rfm,      |
 campaign_roi)                    |
        |                         |
        +------------+------------+
                     v
           Tableau dashboards
```

### Data model

| Layer | Models |
|---|---|
| Staging | `stg_ga4_events`, `stg_crm_customers`, `stg_ad_spend` |
| Intermediate | `int_identity_map`, `int_sessions`, `int_orders`, `int_order_touchpoints` |
| Marts | `fct_sessions`, `fct_orders`, `dim_customer`, `customer_rfm`, `campaign_roi` |

## Repository layout

| Path | Purpose |
|---|---|
| `python/generate_synthetic.py` | Creates CRM customers, the GA identity map and ad-spend seeds |
| `python/attribution.py` | Four attribution models and the comparison table |
| `python/tests/test_attribution.py` | Unit tests for the attribution logic |
| models/staging` | Cleaned GA4 events and seeds |
| models/intermediate` | Identity resolution and order-level touchpoints |
| models/marts` | Sessions, orders, customer profile, RFM segments and campaign ROI |
| models/marts/schema.yml` | Column documentation and dbt tests |
| `docs/dashboard_spec.md` | Tableau dashboard specification |
| `docs/test_plan.md` | Test cases, results and notes |
| `docs/test_results.txt` | Output of dbt, pytest and the attribution run |
| `docs/demo_link.txt` | Links to the published Tableau views |

## Setup

1. Create a Google Cloud project, enable BigQuery, and create a dataset named `customer360`. The GA4 sample is public, so there is nothing to copy.
2. Install the Python requirements: `pip install -r python/requirements.txt`
3. Export a list of purchasing GA4 visitor IDs from BigQuery and save it as `ga_user_ids.csv` in the project root. The generator uses this file to build the identity map.
4. Generate the synthetic seeds: `python python/generate_synthetic.py`. This writes three files into `dbt/seeds/`.
5. Copy `dbt/profiles.yml.example` to `~/.dbt/profiles.yml` and set your project ID.
6. Sign in to Google Cloud: `gcloud auth application-default login`
7. Run the dbt pipeline from the `dbt` folder: `dbt deps`, `dbt seed --full-refresh`, `dbt run`, `dbt test`
8. Export `int_order_touchpoints` from BigQuery as `touchpoints.csv` in the project root, then run `python python/attribution.py --input touchpoints.csv`.
9. Connect Tableau to the CSV outputs and build the views in `docs/dashboard_spec.md`.

## Known limitations

- **Identity link rate is 0%.** The identity map links CRM customers to GA visitors, but none of the linked visitors have matching sessions in the models. All sessions and orders are therefore anonymous, so customer-level results are not yet meaningful.
- **Campaign ROI is not reliable yet.** Campaign names in the ad-spend data do not match the channel names in the touchpoints, so most campaigns show zero conversions and an ROI of -1.0.
- **Two dashboard items are not built:** the model selector, and the budget recommendation scatter.

## Deliverables

| Item | Status |
|---|---|
| Working demo | Done: [Watch Tableau Dashboard](https://public.tableau.com/app/profile/pratik.patil3536) |
| Repository structure, README and setup steps | Done |
| Architecture diagram and data documentation | Done (above and `dbt/models/marts/schema.yml`) |
| Test results and performance notes | Done (`docs/test_plan.md`, `docs/test_results.txt`); run time not recorded |
| 10-minute final presentation | Done (`DA-02_presentation_draft.pptx`) |
| Individual reflection | Done (`docs/reflection.txt`) |
