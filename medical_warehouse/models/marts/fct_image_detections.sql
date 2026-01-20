-- SQLBook: Code
with detections as (

    select
        cast(message_id as bigint) as message_id,
        channel_name,
        image_category,
        confidence_score
    from raw.yolo_detections

),

messages as (

    select
        message_id,
        channel_key,
        date_key,
        view_count
    from {{ ref('fct_messages') }}

)

select
    m.message_id,
    m.channel_key,
    m.date_key,
    d.image_category,
    d.confidence_score,
    m.view_count
from detections d
join messages m
    on d.message_id = m.message_id
