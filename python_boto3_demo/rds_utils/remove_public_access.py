import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, MofNCompleteColumn
import boto3
import os

rds_client = boto3.client('rds')

def remove():    
    os.system('cls||clear')

    print("You selected [bold green]'Check if the RDS Instances have public access and remove it to avoid undesired access'[/bold green].")

    list_public_instances = check_public_access()

    if len(list_public_instances) == 0:
        print("No RDS instances found.")
        input("Press ENTER to continue...")
        return

    print("The following RDS instances have public access and will be removed:")

    for instance_id in list_public_instances:
        print(f"[bold red]- {instance_id}[/bold red]")

    confirm = typer.confirm("Are you sure you want to continue?", abort=True)

    delete_progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        transient=True
    )

    if confirm:
        with delete_progress:
            delete_task = delete_progress.add_task(description="Removing public access...", total=len(list_public_instances))
            for instance_id in list_public_instances:
                remove_public_access(instance_id)
                delete_progress.advance(delete_task)
        print("[bold green]Public access removed successfully![/bold green]")
        input("Press ENTER to continue...")
         

def check_public_access():
    try:

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        )

        with progress:
            check_task = progress.add_task("Checking instances...", total=None)
            ids_public_access = []

            response = rds_client.describe_db_instances()
            instances = response.get('DBInstances', [])
            
            if not instances:
                print("No RDS instances found.")
                return []

            for instance in instances:
                instance_id = instance['DBInstanceIdentifier']
                public_access = instance['PubliclyAccessible']

                if public_access:
                    ids_public_access.append(instance_id)

                        
        return ids_public_access
    
    except Exception as e:
        print(f"Error verifying public access: {str(e)}")


def remove_public_access(instance_id):
    """
    Changes the public access of an RDS instance.
    """
    try:
        response = rds_client.modify_db_instance(
            DBInstanceIdentifier=instance_id,
            PubliclyAccessible=False,
            ApplyImmediately=True
        )
    
    except Exception as e:
        print(f"Error changing public access of instance '{instance_id}': {str(e)}")


