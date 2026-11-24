{{  config(materialized='table')  }}

with filtered_departures as (
    select 
        line_product,
        trip_id,
        last_delay_seconds
    from {{ ref('int_departures_last')  }}
    where
        not last_is_cancelled
        and last_delay_seconds is not null
        and is_observation_complete = 1
)

select 
    line_product,
    count(trip_id) as all_trips,
    count(case when last_delay_seconds < {{  var('delay_threshold_seconds')  }} then 1 end) as punctual_trips,
    punctual_trips / all_trips as punctuality_ratio
from filtered_departures
group by line_product
