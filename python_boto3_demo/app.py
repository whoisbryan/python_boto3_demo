import typer
import os
from rich import print
from s3_utils import remove_public_access as s3_remove_public_access
from rds_utils import remove_public_access as rds_remove_public_access
from ec2_utils import remove_ssm_policy


app = typer.Typer(help="CLI with boto3.")


# Función predeterminada
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    CLI principal con menú interactivo.
    """
    
    if ctx.invoked_subcommand is None:
        while True:
            os.system('cls||clear')
            print("=============== [bold]Menu[/bold] ===============")
            print("1. Check if the s3 buckets have public access and remove it to avoid undesired access.")
            print("2. Check if the RDS Instances have public access and remove it to avoid undesired access")
            print("3. Check if the EC2 account instances have assigned the SSM policy on their roles and remove that policy from all instances")
            print("4. Exit")
            print("====================================")
            option = typer.prompt("Choose an option (1-4)")

            if option == "1":
                s3_remove_public_access.remove()
            elif option == "2":
                rds_remove_public_access.remove()
            elif option == "3":
                remove_ssm_policy.remove()
            elif option == "4":
                print("\nThanks for using this CLI!")
                raise typer.Exit()
            else:
                print("Invalid option. Please, try again.\n")


if __name__ == "__main__":
    app()
