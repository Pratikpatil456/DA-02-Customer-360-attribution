-- RFM scores (5 = best) and a 90-day historical LTV estimate.
with orders as (
    select
        customer_id,
        date_diff(date('{{ var("as_of_date") }}'), max(order_date), day) as recency_days,
        count(*) as frequency,
        sum(revenue) as monetary,
        sum(revenue) / count(*) as avg_order_value
    from {{ ref('fct_orders') }}
    where order_date > date_sub(date('{{ var("as_of_date") }}'), interval 90 day)
    group by customer_id
),
scored as (
    select
        *,
        6 - ntile(5) over (order by recency_days) as r_score,
        ntile(5) over (order by frequency) as f_score,
        ntile(5) over (order by monetary) as m_score
    from orders
)
select
    customer_id,
    recency_days,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    r_score * 100 + f_score * 10 + m_score as rfm_code,
    round(avg_order_value * frequency, 2) as ltv_90d,
    case
        when r_score >= 4 and f_score >= 4 then 'Champions'
        when r_score >= 3 and f_score >= 3 then 'Loyal'
        when r_score >= 4 and f_score <= 2 then 'New or Promising'
        when r_score <= 2 and f_score >= 3 then 'At Risk'
        when r_score <= 2 and f_score <= 2 then 'Hibernating'
        else 'Needs Attention'
    end as segment
from scored
