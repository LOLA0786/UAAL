import json, boto3

class S3ObjectLockStore:
    def __init__(self, bucket, prefix="evidence/"):
        self.bucket = bucket
        self.prefix = prefix
        self.s3 = boto3.client("s3")

    def write(self, key: str, data: dict):
        self.s3.put_object(
            Bucket=self.bucket,
            Key=self.prefix + key,
            Body=json.dumps(data).encode(),
            ContentType="application/json",
            ObjectLockMode="COMPLIANCE"
        )
