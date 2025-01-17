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
            # Obtener las instancias RDS
            response = rds_client.describe_db_instances()
            instances = response.get('DBInstances', [])
            
            if not instances:
                print("No se encontraron instancias RDS.")
                return []

            for instance in instances:
                instance_id = instance['DBInstanceIdentifier']
                public_access = instance['PubliclyAccessible']

                if public_access:
                    ids_public_access.append(instance_id)

                        
        return ids_public_access
    
    except Exception as e:
        print(f"Error al verificar el acceso público: {str(e)}")


def remove_public_access(instance_id):
    """
    Cambia el acceso público de una instancia RDS.
    
    :param instance_id: El identificador de la instancia RDS.
    """
    try:
        response = rds_client.modify_db_instance(
            DBInstanceIdentifier=instance_id,
            PubliclyAccessible=False,
            ApplyImmediately=True  # Aplicar el cambio inmediatamente
        )
    
    except Exception as e:
        print(f"Error al cambiar el acceso público de la instancia '{instance_id}': {str(e)}")


