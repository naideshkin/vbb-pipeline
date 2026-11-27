import os
from datetime import date, datetime, timedelta

from airflow.sdk import dag, task
import requests

CLICKHOUSE_URL = "http://clickhouse:8123/"

def run_query(sql):
    response = requests.post(
        CLICKHOUSE_URL,
        data=sql,
        auth=(
            os.environ["CLICKHOUSE_LOADER_USER"],
            os.environ["CLICKHOUSE_LOADER_PASSWORD"],
        ),
        timeout=300,
    )
    if not response.ok:
        raise RuntimeError(response.text)
    return response.text

@dag(
    schedule="@daily",
    start_date=datetime(2026, 11, 6),
    catchup=True,
    tags=["production"],
    default_args={"retries": 2, "retry_delay": timedelta(seconds=30)},
    max_active_runs=1,
)
def vbb_load():

    @task
    def load_day(ds=None):
       
        run_date = date.fromisoformat(ds)
        load_date = run_date - timedelta(days=1)
        partition_id = load_date.strftime("%Y%m%d")
        run_query(f"ALTER TABLE vbb.raw_departures DROP PARTITION {partition_id}")
        run_query(f"""INSERT INTO vbb.raw_departures (fetched_at, stop_id, source, params, response, source_file)
SELECT
    parseDateTime64BestEffort(JSONExtractString(json, 'fetched_at'), 3, 'UTC'),
    JSONExtractString(json, 'stop_id'),
    JSONExtractString(json, 'source'),
    JSONExtractRaw(json, 'params'),
    JSONExtractRaw(json, 'response'),
    _path
FROM s3(seaweedfs_raw, filename = 'departures/date={load_date}/stop_id=*/*.json.gz', format = 'JSONAsString')""")
    
    load_day()

vbb_load()