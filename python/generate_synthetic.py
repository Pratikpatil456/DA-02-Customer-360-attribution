"""Generate synthetic CRM customers, a GA identity map and ad spend as dbt seeds.

Uses real GA4 visitor IDs from ga_user_ids.csv (project root) when present,
so the identity map actually matches GA4 visitors.

Outputs (into dbt/seeds/):
  crm_customers.csv   customer_id, customer_name, email, country, signup_date
  ga_identity_map.csv user_pseudo_id, customer_id   (about 60% of CRM customers are matched)
  ad_spend.csv        spend_date, channel, campaign, cost, impressions, clicks
"""
import random
from pathlib import Path

import pandas as pd
from faker import Faker

PROJECT_DIR = Path(__file__).resolve().parent.parent
SEED_DIR = PROJECT_DIR / "dbt" / "seeds"
GA_IDS_FILE = PROJECT_DIR / "ga_user_ids.csv"
RNG_SEED = 42
N_CUSTOMERS = 2000
MATCH_RATE = 0.6
CHANNELS = {
    "google_ads": ["brand_search", "shopping_q4", "generic_search"],
    "facebook": ["retargeting", "lookalike_2021"],
    "email": ["newsletter", "abandoned_cart"],
    "affiliate": ["partner_blog"],
}


def load_ga_ids() -> list[str]:
    """Return real GA4 visitor IDs, or fall back to placeholders if the file is missing."""
    if GA_IDS_FILE.exists():
        ids = pd.read_csv(GA_IDS_FILE, dtype={"user_pseudo_id": str})["user_pseudo_id"].dropna().unique().tolist()
        print(f"Using {len(ids)} real GA4 visitor IDs from {GA_IDS_FILE.name}")
        return ids
    print("ga_user_ids.csv not found; using placeholder IDs (links will not match GA4)")
    return [f"ga_client_{n:06d}" for n in range(1, 5001)]


def build_customers(fake: Faker, rng: random.Random, ga_ids: list[str]):
    customers = []
    for i in range(N_CUSTOMERS):
        customers.append({
            "customer_id": f"C{i + 1:05d}",
            "customer_name": fake.name(),
            "email": fake.unique.email(),
            "country": fake.country_code(),
            "signup_date": fake.date_between(start_date="-3y", end_date="-1m").isoformat(),
        })

    # Link about MATCH_RATE of customers to a distinct GA visitor (no repeats).
    n_matched = min(int(N_CUSTOMERS * MATCH_RATE), len(ga_ids))
    matched_customers = rng.sample([c["customer_id"] for c in customers], n_matched)
    matched_visitors = rng.sample(ga_ids, n_matched)
    identity = pd.DataFrame({"user_pseudo_id": matched_visitors, "customer_id": matched_customers})
    return pd.DataFrame(customers), identity


def build_ad_spend(rng: random.Random):
    rows = []
    for day in pd.date_range("2020-11-01", "2021-01-31"):
        for channel, campaigns in CHANNELS.items():
            for campaign in campaigns:
                impressions = rng.randint(5_000, 60_000)
                clicks = int(impressions * rng.uniform(0.01, 0.05))
                cost = round(clicks * rng.uniform(0.4, 1.8), 2)
                rows.append({
                    "spend_date": day.date().isoformat(),
                    "channel": channel,
                    "campaign": campaign,
                    "cost": cost,
                    "impressions": impressions,
                    "clicks": clicks,
                })
    return pd.DataFrame(rows)


def main():
    rng = random.Random(RNG_SEED)
    fake = Faker()
    Faker.seed(RNG_SEED)
    SEED_DIR.mkdir(parents=True, exist_ok=True)

    ga_ids = load_ga_ids()
    customers, identity = build_customers(fake, rng, ga_ids)
    spend = build_ad_spend(rng)

    customers.to_csv(SEED_DIR / "crm_customers.csv", index=False)
    identity.to_csv(SEED_DIR / "ga_identity_map.csv", index=False)
    spend.to_csv(SEED_DIR / "ad_spend.csv", index=False)
    print(f"customers={len(customers)} identity_links={len(identity)} spend_rows={len(spend)}")


if __name__ == "__main__":
    main()
