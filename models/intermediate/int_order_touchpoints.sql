-- All sessions for the same customer in the N days before each order. Input to attribution.
select
    o.order_id,
    o.customer_id,
    o.order_ts,
    o.revenue,
    s.session_start_ts as touch_ts,
    s.user_pseudo_id,
    s.ga_session_id,
    coalesce(s.campaign, s.source_medium) as channel
from {{ ref('int_orders') }} o
join {{ ref('int_identity_map') }} i on i.customer_id = o.customer_id
join {{ ref('int_sessions') }} s on s.user_pseudo_id = i.user_pseudo_id
where s.session_start_ts <= o.order_ts
  and s.session_start_ts >= timestamp_sub(o.order_ts, interval {{ var('lookback_days') }} day)
