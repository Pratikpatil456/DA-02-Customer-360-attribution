-- One row per completed purchase with a known revenue value.
select
    order_id,
    customer_id,
    order_ts,
    date(order_ts) as order_date,
    revenue
from {{ ref('int_orders') }}
where revenue is not null