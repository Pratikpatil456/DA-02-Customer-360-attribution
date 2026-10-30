import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from attribution import attribute, first_touch, last_touch, linear, time_decay  # noqa: E402


@pytest.fixture
def touches():
    return pd.DataFrame({
        "order_id": ["o1", "o1", "o1", "o2"],
        "channel": ["email", "facebook", "google", "google"],
        "touch_ts": ["2021-01-01", "2021-01-05", "2021-01-09", "2021-01-08"],
        "order_ts": ["2021-01-10"] * 4,
        "revenue": [90.0, 90.0, 90.0, 50.0],
    })


def _prep(df):
    df = df.copy()
    df["touch_ts"] = pd.to_datetime(df["touch_ts"], utc=True)
    df["order_ts"] = pd.to_datetime(df["order_ts"], utc=True)
    return df


def test_first_touch_gives_full_credit_to_earliest(touches):
    assert first_touch(_prep(touches)).tolist() == [1.0, 0.0, 0.0, 1.0]


def test_last_touch_gives_full_credit_to_latest(touches):
    assert last_touch(_prep(touches)).tolist() == [0.0, 0.0, 1.0, 1.0]


def test_linear_splits_evenly(touches):
    w = linear(_prep(touches))
    assert w.loc[0] == pytest.approx(1 / 3)
    assert w.loc[3] == pytest.approx(1.0)


def test_time_decay_weights_sum_to_one_per_order(touches):
    w = time_decay(_prep(touches), half_life_days=7)
    assert w[:3].sum() == pytest.approx(1.0)
    assert w[3] == pytest.approx(1.0)
    assert w[2] > w[1] > w[0]


def test_revenue_is_conserved_by_every_model(touches):
    result = attribute(touches)
    totals = result[["first_touch", "last_touch", "linear", "time_decay"]].sum()
    assert totals.tolist() == pytest.approx([140.0] * 4, abs=0.05)
