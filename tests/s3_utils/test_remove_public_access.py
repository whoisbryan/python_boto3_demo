import pytest
from moto import mock_aws
import boto3

from python_boto3_demo.s3_utils.remove_public_access import (
    get_aws_account_id,
    get_buckets,
    get_bucket_permissions,
    filter_buckets_with_public_access,
    remove_public_access
)


@mock_aws
def test_get_aws_account_id():
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]
    
    assert get_aws_account_id() == account_id


@mock_aws
def test_get_buckets():
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket="test-bucket-1")
    s3_client.create_bucket(Bucket="test-bucket-2")
    
    buckets = get_buckets(s3_client)
    assert "test-bucket-1" in buckets
    assert "test-bucket-2" in buckets
    assert len(buckets) == 2


@mock_aws
def test_get_bucket_permissions():
    account_id = get_aws_account_id()
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket="test-bucket")
    s3_client.put_public_access_block(
        Bucket="test-bucket",
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': False,  
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
    
    permissions = get_bucket_permissions(s3_client, "test-bucket", account_id)
    assert permissions == {
        'BlockPublicAcls': True,
        'IgnorePublicAcls': False,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }


def test_filter_buckets_with_public_access():
    buckets_permissions = {
        "bucket-1": {
            'BlockPublicAcls': True,
            'IgnorePublicAcls': False,  
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
        "bucket-2": {
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    }
    
    filtered_buckets = filter_buckets_with_public_access(buckets_permissions)
    assert "bucket-1" in filtered_buckets
    assert "bucket-2" not in filtered_buckets
    assert len(filtered_buckets) == 1


@mock_aws
def test_remove_public_access():
    account_id = get_aws_account_id()
    s3_client = boto3.client('s3')
    s3_client.create_bucket(Bucket="test-bucket")
    s3_client.put_public_access_block(
        Bucket="test-bucket",
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False,  
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False
        }
    )

    remove_public_access(s3_client, "test-bucket", account_id)
    
    permissions = s3_client.get_public_access_block(Bucket="test-bucket")['PublicAccessBlockConfiguration']
    assert permissions == {
        'BlockPublicAcls': True,
        'IgnorePublicAcls': True,
        'BlockPublicPolicy': True,
        'RestrictPublicBuckets': True
    }
