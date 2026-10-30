select customer_id, customer_name, email, country, signup_date
from {{ ref('crm_customers') }}
