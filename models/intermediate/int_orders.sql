-- One row per completed purchase, with the customer it belongs to.
-- Deduplicated: if a transaction_id appears more than once, keep the earliest row.
with orders_raw as (
    select
        e.transaction_id as order_id,
        e.user_pseudo_id,
        i.customer_id,
        min(e.event_ts) as order_ts,
        max(e.purchase_revenue) as revenue
    from {{ ref('stg_ga4_events') }} e
    join {{ ref('int_identity_map') }} i using (user_pseudo_id)
    where e.event_name = 'purchase' and e.transaction_id is not null
    group by e.transaction_id, e.user_pseudo_id, i.customer_id
)
select order_id, user_pseudo_id, customer_id, order_ts, revenue
from (
    select
        *,
        row_number() over (partition by order_id order by order_ts) as rn
    from orders_raw
)
where rn = 1