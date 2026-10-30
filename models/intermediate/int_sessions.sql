-- One row per GA4 session with its start timestamp and traffic source.
select
    user_pseudo_id,
    ga_session_id,
    min(event_ts) as session_start_ts,
    any_value(source) as source,
    any_value(medium) as medium,
    any_value(campaign) as campaign,
    concat(coalesce(any_value(source), '(direct)'), ' / ', coalesce(any_value(medium), '(none)')) as source_medium,
    countif(event_name = 'purchase') > 0 as has_purchase
from {{ ref('stg_ga4_events') }}
where ga_session_id is not null
group by user_pseudo_id, ga_session_id
