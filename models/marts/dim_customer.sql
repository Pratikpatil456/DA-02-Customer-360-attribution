select
    c.customer_id,
    c.customer_name,
    c.email,
    c.country,
    c.signup_date,
    count(distinct i.user_pseudo_id) as linked_devices
from {{ ref('stg_crm_customers') }} c
left join {{ ref('ga_identity_map') }} i on i.customer_id = c.customer_id
group by 1, 2, 3, 4, 5
