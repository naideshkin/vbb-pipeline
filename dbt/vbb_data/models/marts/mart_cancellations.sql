{{  config(materialized='table')  }}

with trips as (
    select 
        line_product,
        trip_id,
        last_is_cancelled
    from {{ ref('int_departures_last')  }}
)

select 
    line_product,
    count(trip_id) as all_trips,
    countIf(last_is_cancelled = 1) as cancelled_trips,
    cancelled_trips / all_trips as cancelled_ratio
from trips
group by line_product
