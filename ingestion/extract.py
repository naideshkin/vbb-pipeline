import json
import os
from datetime import datetime, timezone
import gzip

import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://v6.vbb.transport.rest"
BUCKET = "raw"
DURATION_MIN = 30
STOPS = {
    "900100003": "S+U Alexanderplatz",
    "900054105": "S+U Innsbrucker Platz",
    "900023201": "S+U Zoologischer Garten",
}

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET_KEY"],
    region_name="us-east-1",
)


def build_key(stop_id: str, fetched_at: datetime) -> str:
    return f"departures/date={fetched_at:%Y-%m-%d}/stop_id={stop_id}/{fetched_at:%Y%m%dT%H%M%SZ}.json.gz"


def extract_stop(stop_id: str) -> str:
    fetched_at = datetime.now(timezone.utc)  # 1. note the time we ask
    params = {"duration": DURATION_MIN}
    resp = requests.get(
        f"{BASE_URL}/stops/{stop_id}/departures", params=params, timeout=30
    )
    resp.raise_for_status()  # 2. crash loudly on HTTP errors

    envelope = {  # 3. wrap the answer
        "fetched_at": fetched_at.isoformat(),
        "stop_id": stop_id,
        "source": resp.url,
        "params": params,
        "response": resp.json(),
    }

    key = build_key(stop_id, fetched_at)  # 4. save, never overwrite
    body = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=gzip.compress(body),  # compress before uploading
        ContentType="application/gzip",
    )
    return key


if __name__ == "__main__":
    for stop_id, name in STOPS.items():
        key = extract_stop(stop_id)
        print(f"{name} -> {key}")
