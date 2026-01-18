-- SQLBook: Code
select distinct
    to_char(message_date, 'YYYYMMDD')::int as date_key,
    message_date::date as full_date,
    extract(dow from message_date) as day_of_week,
    extract(week from message_date) as week_of_year,
    extract(month from message_date) as month,
    extract(quarter from message_date) as quarter,
    extract(year from message_date) as year,
    case when extract(dow from message_date) in (0,6) then true else false end as is_weekend
from {{ ref('stg_telegram_messages') }}
