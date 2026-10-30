select
    spend_date,
    channel,
    campaign,
    cast(cost as float64) as cost,
    cast(impressions as int64) as impressions,
    cast(clicks as int64) as clicks
from {{ ref('ad_spend') }}
