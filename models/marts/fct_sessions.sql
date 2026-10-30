select
    s.user_pseudo_id,
    s.ga_session_id,
    i.customer_id,
    i.is_known_customer,
    s.session_start_ts,
    date(s.session_start_ts) as session_date,
    s.source,
    s.medium,
    s.campaign,
    s.source_medium,
    s.has_purchase
from {{ ref('int_sessions') }} s
join {{ ref('int_identity_map') }} i using (user_pseudo_id)
