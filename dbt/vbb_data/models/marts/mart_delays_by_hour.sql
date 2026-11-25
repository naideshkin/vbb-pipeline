{{  config(materialized='table')  }}

with filtered_trips as (
    select 
        trip_id,
        last_delay_seconds,
        toHour(toTimeZone(planned_when, 'Europe/Berlin')) as hour_planned,
        toDayOfWeek(toTimeZone(planned_when, 'Europe/Berlin')) as day_planned
    from {{ ref('int_departures_last')  }}
    where
        not last_is_cancelled
        and last_delay_seconds is not null
        and is_observation_complete = 1
)

select 
    day_planned,
    hour_planned,
    count(trip_id) as all_trips,
    count(case when last_delay_seconds < {{  var('delay_threshold_seconds')  }} then 1 end) as punctual_trips,
    punctual_trips / all_trips as punctuality_ratio
from filtered_trips
group by day_planned, hour_planned
having all_trips >= {{ var('min_trips_per_group') }}
order by day_planned, hour_planned
