with grouped_departures as (
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
        argMax(is_cancelled, fetched_at) as last_is_cancelled
    from {{ ref('stg_departures') }}
    group by
        trip_id,
        stop_id
),

with_expected_departure as (
    select
        *,
        addSeconds(planned_when, last_delay_seconds) as expected_departure
    from grouped_departures
),

with_gap as (
    select
        *,
        dateDiff('minute', expected_departure, last_fetched_at) as gap_minutes
    from with_expected_departure
)

select
    trip_id,
    stop_id,
    queried_stop_id,
    line_name,
    line_product,
    direction,
    planned_when,
    last_fetched_at,
    last_delay_seconds,
    last_is_cancelled,
    expected_departure,
    gap_minutes,
    case
        when expected_departure is null then null
        when gap_minutes >= -5 then 1
        else 0
    end as is_observation_complete
from with_gap