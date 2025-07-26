import os, mimetypes, boto3

bucket   = os.getenv("S3_BUCKET")
_region  = os.getenv("AWS_REGION", "us-east-1")

s3 = boto3.client(
    "s3",
    region_name=_region,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

def upload(local_path: str, key: str) -> str:
    content_type, _ = mimetypes.guess_type(local_path)
    s3.upload_file(local_path, bucket, key, ExtraArgs={"ContentType": content_type or "application/octet-stream"})
    return f"s3://{bucket}/{key}"
