from datetime import datetime, timedelta

from airflow.sdk import dag, task

from ingestion.extract import extract_stop, STOPS


@dag(
    schedule="*/2 * * * *",  # cron: every 2 minutes
    start_date=datetime(2026, 11, 10),  # first time slot it may run for
    catchup=False,  # don't run all slots between start_date and now
    tags=["production"],
    default_args={"retries": 2, "retry_delay": timedelta(seconds=30)},
)
def vbb_extract():
    
    @task
    def extract_stop_task(stop_id):
        return extract_stop(stop_id)
       
       
    for stop_id in STOPS:
        extract_stop_task.override(task_id=f"extract_{stop_id}")(stop_id)

vbb_extract()
