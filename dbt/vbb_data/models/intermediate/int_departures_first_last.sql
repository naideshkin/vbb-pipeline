with grouped_departures as (
    select
        trip_id,
        stop_id,
        min(fetched_at) as first_fetched_at,
        argMin(delay_seconds, fetched_at) as first_delay_seconds,
        argMax(delay_seconds, fetched_at) as last_delay_seconds
    from {{ ref('stg_departures') }}
    group by
        trip_id,
        stop_id
)

select
    trip_id,
    stop_id,
    first_fetched_at,
    first_delay_seconds,
    last_delay_seconds,
    last_delay_seconds - first_delay_seconds as delay_error_seconds
from grouped_departures
where first_delay_seconds is not null and last_delay_seconds is not null