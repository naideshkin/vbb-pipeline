{{ config(materialized='table') }}

with trips as (
    select 
        int_departures_first_last.trip_id as trip_id, 
        int_departures_last.line_product as line_product,
        int_departures_first_last.first_delay_seconds as first_delay_seconds,
        int_departures_first_last.last_delay_seconds as last_delay_seconds,
        int_departures_first_last.delay_error_seconds as delay_error_seconds
    from {{  ref('int_departures_first_last')  }} as int_departures_first_last
    join {{  ref('int_departures_last') }} as int_departures_last
    on int_departures_first_last.trip_id = int_departures_last.trip_id
    and int_departures_first_last.stop_id = int_departures_last.stop_id
)

select 
    count(trip_id) as all_trips, 
    line_product,
    countIf(first_delay_seconds = last_delay_seconds) as unchanged_trips, 
    unchanged_trips / all_trips as unchanged_ratio, 
    avg(abs(delay_error_seconds)) as avg_abs_error_seconds, 
    quantile(0.9)(abs(delay_error_seconds)) as p90_abs_error_seconds, 
    avg(delay_error_seconds) as avg_error_seconds
from trips
group by line_product