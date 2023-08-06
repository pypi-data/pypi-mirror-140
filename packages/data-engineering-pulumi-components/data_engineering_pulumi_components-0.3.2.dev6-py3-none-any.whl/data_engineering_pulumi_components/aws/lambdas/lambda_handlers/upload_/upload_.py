import json
import boto3
import os


def handler(event, context):
    s3 = boto3.client("s3")

    bucket_name = os.environ["bucketname"]

    file_name = event["queryStringParameters"]["filename"]
    fields = {"x-amz-server-side-encryption": "AES256"}
    conditions = [{"x-amz-server-side-encryption": "AES256"}]

    URL = s3.generate_presigned_post(
        Bucket=bucket_name,
        Key=file_name,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=3600,
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"URL": URL}),
    }
