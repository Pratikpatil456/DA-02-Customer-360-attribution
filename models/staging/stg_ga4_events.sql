-- One row per GA4 event, with session keys and traffic source pulled out of event_params.
select
    user_pseudo_id,
    event_name,
    event_timestamp,
    timestamp_micros(event_timestamp) as event_ts,
    (select value.int_value from unnest(event_params) where key = 'ga_session_id') as ga_session_id,
    (select value.string_value from unnest(event_params) where key = 'source') as source,
    (select value.string_value from unnest(event_params) where key = 'medium') as medium,
    (select value.string_value from unnest(event_params) where key = 'campaign') as campaign,
    ecommerce.transaction_id as transaction_id,
    ecommerce.purchase_revenue as purchase_revenue
from {{ source('ga4', 'events_*') }}
where _table_suffix between '20201101' and '20210131'
