import os
from pathlib import Path
import boto3
from dotenv import load_dotenv

load_dotenv()  # reads .env into environment variables

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    aws_access_key_id=os.environ["S3_ACCESS_KEY"],
    aws_secret_access_key=os.environ["S3_SECRET_KEY"],
    region_name="us-east-1",
)

BUCKET = "raw"

# 1. The bucket must already exist (created at setup, not by the pipeline)
s3.head_bucket(Bucket=BUCKET)  # raises an error if it's missing or we have no access
print("Bucket is reachable:", BUCKET)

# 2. Upload one sample file
sample = sorted(Path("docs/samples").glob("*.json"))[0]
key = f"test/{sample.name}"
s3.upload_file(str(sample), BUCKET, key)
print("Uploaded:", key)

# 3. List what's in the bucket under "test/"
for obj in s3.list_objects_v2(Bucket=BUCKET, Prefix="test/").get("Contents", []):
    print("  found:", obj["Key"], obj["Size"], "bytes")

# 4. Read it back and compare with the local file
body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
print("Same size as local file:", len(body) == sample.stat().st_size)
