import gzip, json, os
import boto3
from dotenv import load_dotenv

load_dotenv()
s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET_KEY"],
    region_name="us-east-1",
)

# find the newest file under departures/
objs = s3.list_objects_v2(Bucket="raw", Prefix="departures/")["Contents"]
latest = max(objs, key=lambda o: o["LastModified"])

# download, decompress, parse
raw = s3.get_object(Bucket="raw", Key=latest["Key"])["Body"].read()
data = json.loads(gzip.decompress(raw))

print(latest["Key"])
print(
    f"{latest['Size']:,} bytes compressed -> {len(gzip.decompress(raw)):,} bytes as JSON"
)
print(
    "fetched_at:",
    data["fetched_at"],
    "| departures:",
    len(data["response"]["departures"]),
)
