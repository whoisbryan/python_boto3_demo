import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, MofNCompleteColumn
import boto3
import os


def remove():
    """
    Check and remove public permissions on S3 buckets.
    """
    os.system('cls||clear')

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    )

    print("You selected [bold green]'Check if the s3 buckets have public access and remove it to avoid undesired access'[/bold green].")

    s3_client = boto3.client('s3')
    account_id = get_aws_account_id()
    buckets = get_buckets(s3_client)

    with progress:
        get_buckets_task = progress.add_task(description="Getting bucket permissions...", total=None)
        buckets_permissions = {
            bucket: get_bucket_permissions(s3_client, bucket, account_id)
            for bucket in buckets
        }
        progress.remove_task(get_buckets_task)

    filtered_buckets = filter_buckets_with_public_access(buckets_permissions)

    if not filtered_buckets:
        print("[bold green]No buckets with public access found![/bold green]")
        input("Press ENTER to continue...")
        return

    print("The following S3 buckets have public access and will be updated:")
    for bucket in filtered_buckets.keys():
        print(f"[bold red] - {bucket}[/bold red]")

    confirm = typer.confirm("Are you sure you want to continue?", abort=True)

    delete_progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        transient=True
    )

    if confirm:
        with delete_progress:
            task = delete_progress.add_task(description="Removing public access...", total=len(filtered_buckets))
            for bucket in filtered_buckets.keys():
                remove_public_access(s3_client, bucket, account_id)
                delete_progress.advance(task)
        print("[bold green]Public access removed successfully![/bold green]")
        input("Press ENTER to continue...")


def get_aws_account_id():
    """
    Gets the current AWS account ID.
    """
    return boto3.client('sts').get_caller_identity().get('Account')


def get_buckets(s3_client):
    """
    Gets the list of bucket names.
    """
    return [bucket['Name'] for bucket in s3_client.list_buckets().get('Buckets')]


def get_bucket_permissions(s3_client, bucket, account_id):
    """
    Gets the public access settings of a bucket.
    """
    return s3_client.get_public_access_block(
        Bucket=bucket,
        ExpectedBucketOwner=account_id
    ).get('PublicAccessBlockConfiguration')


def filter_buckets_with_public_access(buckets_permissions):
    """
    Filter buckets that have at least one public permission.
    """
    return {
        bucket: config
        for bucket, config in buckets_permissions.items()
        if any(value is False for value in config.values())
    }


def remove_public_access(s3_client, bucket, account_id):
    """
    Configure the bucket to block public access.
    """
    s3_client.put_public_access_block(
        Bucket=bucket,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        },
        ExpectedBucketOwner=account_id
    )