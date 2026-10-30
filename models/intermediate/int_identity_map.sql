-- Identity resolution: GA client -> CRM customer. Unmatched GA clients stay anonymous.
with ga_ids as (
    select distinct user_pseudo_id from {{ ref('stg_ga4_events') }}
)
select
    g.user_pseudo_id,
    coalesce(m.customer_id, concat('anon_', g.user_pseudo_id)) as customer_id,
    m.customer_id is not null as is_known_customer
from ga_ids g
left join {{ ref('ga_identity_map') }} m using (user_pseudo_id)
