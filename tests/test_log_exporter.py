import os
import tempfile
import shutil
import time
import pytest
from unittest import mock
from app.services import log_exporter

def test_rotate_log_daily_and_hourly():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, 'audit.log')
        with open(log_path, 'w') as f:
            f.write('test')
        daily = log_exporter.rotate_log(log_path, 'daily')
        assert os.path.exists(daily)
        with open(log_path, 'w') as f:
            f.write('test2')
        hourly = log_exporter.rotate_log(log_path, 'hourly')
        assert os.path.exists(hourly)

def test_cleanup_old_logs():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, 'audit.log')
        old_file = log_path + '.20200101'
        with open(old_file, 'w') as f:
            f.write('old')
        os.utime(old_file, (time.time() - 40*86400, time.time() - 40*86400))
        log_exporter.cleanup_old_logs(log_path, retention_days=30)
        assert not os.path.exists(old_file)

def test_upload_to_s3_dry_run():
    with mock.patch('boto3.client') as mock_boto:
        log_exporter.upload_to_s3('file', 'bucket', 'key', 'id', 'secret', 'region', dry_run=True)
        mock_boto.assert_not_called()

def test_upload_to_gcs_dry_run():
    with mock.patch('google.cloud.storage.Client') as mock_gcs:
        log_exporter.upload_to_gcs('file', 'bucket', 'key', 'creds.json', dry_run=True)
        mock_gcs.from_service_account_json.assert_not_called()

def test_upload_to_azure_dry_run():
    with mock.patch('azure.storage.blob.BlobServiceClient') as mock_az:
        log_exporter.upload_to_azure('file', 'container', 'key', 'connstr', dry_run=True)
        mock_az.from_connection_string.assert_not_called()
