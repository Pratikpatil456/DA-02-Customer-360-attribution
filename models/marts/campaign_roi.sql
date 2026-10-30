-- Channel ROI using last-touch attribution (python/attribution.py compares all four models).
with last_touch as (
    select
        order_id,
        revenue,
        channel,
        row_number() over (partition by order_id order by touch_ts desc) as rn
    from {{ ref('int_order_touchpoints') }}
),
attributed as (
    select channel, sum(revenue) as attributed_revenue, count(distinct order_id) as conversions
    from last_touch
    where rn = 1
    group by channel
),
spend as (
    select campaign as channel, sum(cost) as cost, sum(clicks) as clicks, sum(impressions) as impressions
    from {{ ref('stg_ad_spend') }}
    group by campaign
)
select
    s.channel,
    s.cost,
    s.impressions,
    s.clicks,
    coalesce(a.conversions, 0) as conversions,
    coalesce(a.attributed_revenue, 0) as attributed_revenue,
    safe_divide(coalesce(a.attributed_revenue, 0) - s.cost, s.cost) as roi,
    safe_divide(s.cost, coalesce(a.conversions, 0)) as cost_per_acquisition
from spend s
left join attributed a on a.channel = s.channel
