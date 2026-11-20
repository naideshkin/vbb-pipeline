select 
    fetched_at,
    stop_id as queried_stop_id,
    JSONExtractString(dep, 'tripId') as trip_id,
    JSONExtractString(dep, 'stop', 'id') as stop_id,
    JSONExtractString(dep, 'line', 'name') as line_name,
    JSONExtractString(dep, 'line', 'product') as line_product,
    JSONExtractString(dep, 'direction') as direction,
    parseDateTimeBestEffortOrNull(JSONExtract(dep, 'plannedWhen', 'Nullable(String)'), 'UTC') as planned_when,
    parseDateTimeBestEffortOrNull(JSONExtract(dep, 'when', 'Nullable(String)'), 'UTC') as observed_when,
    JSONExtract(dep, 'delay', 'Nullable(Int32)') as delay_seconds,
    nullIf(JSONExtractString(dep, 'plannedPlatform'), '') as planned_platform,
    nullIf(JSONExtractString(dep, 'platform'), '') as platform,
    JSONExtractBool(dep, 'cancelled') as is_cancelled
from 
    {{ source('vbb_pipeline', 'raw_departures') }}

ARRAY JOIN JSONExtractArrayRaw(response, 'departures') as dep