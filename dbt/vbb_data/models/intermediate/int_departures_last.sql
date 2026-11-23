select
    trip_id,
    stop_id,
    any(queried_stop_id) as queried_stop_id,
    any(line_name) as line_name,
    any(line_product) as line_product,
    any(direction) as direction,
    any(planned_when) as planned_when,
    max(fetched_at) as last_fetched_at,
    argMax(delay_seconds, fetched_at) as last_delay_seconds,
    argMax(is_cancelled, fetched_at) as last_is_cancelled,
    addSeconds(planned_when, last_delay_seconds) as expected_departure,
    dateDiff('minute', expected_departure, last_fetched_at) as gap_minutes,
    case when gap_minutes >= -5 then 1
         when expected_departure is Null then Null
         else 0 
        end as is_observation_complete
from 
    {{ ref('stg_departures')}}
group by 
    trip_id,
    stop_id