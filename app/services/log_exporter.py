import os
import sys
import shutil
import datetime
import time
import argparse

def rotate_log(log_path, rotation="daily"):
    now = datetime.datetime.utcnow()
    if rotation == "hourly":
        suffix = now.strftime("%Y%m%d_%H")
    else:
        suffix = now.strftime("%Y%m%d")
    rotated = f"{log_path}.{suffix}"
    if os.path.exists(log_path):
        shutil.copy2(log_path, rotated)
        open(log_path, 'w').close()
    return rotated

def upload_to_s3(file_path, bucket, key, aws_access_key, aws_secret_key, region, dry_run=False):
    if dry_run:
        print(f"[DRY RUN] Would upload {file_path} to S3 bucket {bucket} as {key}")
        return
    import boto3
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region)
    s3.upload_file(file_path, bucket, key)

def upload_to_gcs(file_path, bucket, key, gcp_creds_json, dry_run=False):
    if dry_run:
        print(f"[DRY RUN] Would upload {file_path} to GCS bucket {bucket} as {key}")
        return
    from google.cloud import storage
    client = storage.Client.from_service_account_json(gcp_creds_json)
    bucket = client.bucket(bucket)
    blob = bucket.blob(key)
    blob.upload_from_filename(file_path)

def upload_to_azure(file_path, container, key, conn_str, dry_run=False):
    if dry_run:
        print(f"[DRY RUN] Would upload {file_path} to Azure container {container} as {key}")
        return
    from azure.storage.blob import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service_client.get_blob_client(container=container, blob=key)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

def cleanup_old_logs(log_path, retention_days):
    cutoff = time.time() - retention_days * 86400
    for fname in os.listdir(os.path.dirname(log_path)):
        if fname.startswith(os.path.basename(log_path) + "."):
            fpath = os.path.join(os.path.dirname(log_path), fname)
            if os.path.getmtime(fpath) < cutoff:
                os.remove(fpath)
                print(f"Deleted expired log: {fpath}")

def main():
    parser = argparse.ArgumentParser(description="Export and rotate audit logs to cloud storage.")
    parser.add_argument('--dry-run', action='store_true', help='Print actions without uploading')
    parser.add_argument('--interval', choices=['daily', 'hourly'], help='Override log rotation interval')
    parser.add_argument('--target', choices=['s3', 'gcs', 'azure'], help='Override upload provider')
    args = parser.parse_args()

    log_path = os.getenv("AUDIT_LOG_PATH", "logs/audit.log")
    rotation = args.interval or os.getenv("AUDIT_LOG_ROTATION", "daily")
    provider = args.target or os.getenv("AUDIT_LOG_EXPORT_PROVIDER", "none")
    retention = int(os.getenv("AUDIT_LOG_EXPORT_RETENTION_DAYS", "30"))
    rotated = rotate_log(log_path, rotation)
    if provider == "s3":
        upload_to_s3(rotated, os.getenv("S3_BUCKET"), os.path.basename(rotated), os.getenv("AWS_ACCESS_KEY_ID"), os.getenv("AWS_SECRET_ACCESS_KEY"), os.getenv("AWS_REGION"), dry_run=args.dry_run)
    elif provider == "gcs":
        upload_to_gcs(rotated, os.getenv("GCS_BUCKET"), os.path.basename(rotated), os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), dry_run=args.dry_run)
    elif provider == "azure":
        upload_to_azure(rotated, os.getenv("AZURE_CONTAINER"), os.path.basename(rotated), os.getenv("AZURE_STORAGE_CONNECTION_STRING"), dry_run=args.dry_run)
    else:
        print("No cloud provider configured. Skipping upload.")
    cleanup_old_logs(log_path, retention)

if __name__ == "__main__":
    main()
