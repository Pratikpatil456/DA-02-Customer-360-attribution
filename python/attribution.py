"""Attribution models over an order-touchpoint table.

Input columns: order_id, channel, touch_ts, order_ts, revenue
Each order's revenue is split across its touchpoints by the chosen model.
"""
import argparse

import numpy as np
import pandas as pd


def first_touch(touches: pd.DataFrame) -> pd.Series:
    w = pd.Series(0.0, index=touches.index)
    w.loc[touches.sort_values("touch_ts").groupby("order_id").head(1).index] = 1.0
    return w


def last_touch(touches: pd.DataFrame) -> pd.Series:
    w = pd.Series(0.0, index=touches.index)
    w.loc[touches.sort_values("touch_ts").groupby("order_id").tail(1).index] = 1.0
    return w


def linear(touches: pd.DataFrame) -> pd.Series:
    n = touches.groupby("order_id")["channel"].transform("count")
    return 1.0 / n


def time_decay(touches: pd.DataFrame, half_life_days: float = 7.0) -> pd.Series:
    age_days = (touches["order_ts"] - touches["touch_ts"]).dt.total_seconds() / 86400.0
    raw = np.power(0.5, age_days / half_life_days)
    total = raw.groupby(touches["order_id"]).transform("sum")
    return raw / total


MODELS = {
    "first_touch": first_touch,
    "last_touch": last_touch,
    "linear": linear,
    "time_decay": time_decay,
}


def attribute(touches: pd.DataFrame) -> pd.DataFrame:
    """Return revenue credited to each channel under every model."""
    touches = touches.reset_index(drop=True).copy()
    touches["touch_ts"] = pd.to_datetime(touches["touch_ts"], utc=True)
    touches["order_ts"] = pd.to_datetime(touches["order_ts"], utc=True)
    out = {}
    for name, fn in MODELS.items():
        weights = fn(touches)
        out[name] = (touches["revenue"] * weights).groupby(touches["channel"]).sum()
    result = pd.DataFrame(out).fillna(0.0)
    return result.sort_values("last_touch", ascending=False).round(2)


def main():
    parser = argparse.ArgumentParser(description="Compare attribution models.")
    parser.add_argument("--input", required=True, help="CSV exported from int_order_touchpoints")
    parser.add_argument("--output", default="attribution_comparison.csv")
    args = parser.parse_args()
    result = attribute(pd.read_csv(args.input))
    result.to_csv(args.output)
    print(result.to_string())


if __name__ == "__main__":
    main()
