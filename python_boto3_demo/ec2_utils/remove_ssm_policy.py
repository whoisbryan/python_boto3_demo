import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, MofNCompleteColumn
import boto3
import os


ec2_client = boto3.client('ec2')
iam_client = boto3.client('iam')

SSM_POLICY_ARN = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"


def remove():
    os.system('cls||clear')

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        transient=True
    )
    print("You selected [bold green]'Check if the EC2 account instances have assigned the SSM policy on their roles and remove that policy from all instances'[/bold green].")
    
    instance_profiles = get_instance_profiles()

    if not instance_profiles:
        print("No instances with IAM instance profiles found.")
        input("Press ENTER to continue...")
        return

    print("The following EC2 instances have SSM policy on their roles and will be removed:")

    for instance_id, _ in instance_profiles:
        print(f"[bold red]- {instance_id}")
    
    confirm = typer.confirm("Are you sure you want to continue?", abort=True)

    if confirm:
        with progress:
            task = progress.add_task("Removing SSM Policy", total=(len(instance_profiles)))
            for instance_id, profile_name in instance_profiles:
                check_and_remove_ssm_policy(profile_name)
                progress.advance(task)
        print("[bold green]SSM policy removed successfully![/bold green]")
        input("Press ENTER to continue...")


def get_instance_profiles():
    """
    Get all EC2 instances and their associated IAM instance profiles.
    """
    instance_profiles = []

    try:

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        )

        with progress:
            task = progress.add_task("Getting intances profiles...", total=None)
            response = ec2_client.describe_instances()
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instance_id = instance['InstanceId']
                    iam_instance_profile = instance.get('IamInstanceProfile')
                    if iam_instance_profile:
                        profile_arn = iam_instance_profile['Arn']
                        profile_name = profile_arn.split("/")[-1]
                        instance_profiles.append((instance_id, profile_name))

        return instance_profiles

    except Exception as e:
        print(f"Error fetching EC2 instances: {str(e)}")
        return []


def check_and_remove_ssm_policy(profile_name):
    """
    Check if the instance profile's role has the SSM policy and detach it.
    """
    try:

        response = iam_client.get_instance_profile(InstanceProfileName=profile_name)
        roles = response['InstanceProfile']['Roles']

        for role in roles:
            role_name = role['RoleName']


            attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

            for policy in attached_policies:
                if policy['PolicyArn'] == SSM_POLICY_ARN:
                    iam_client.detach_role_policy(RoleName=role_name, PolicyArn=SSM_POLICY_ARN)
                    break
            else:

                return False
    except Exception as e:
        print(f"Error processing instance profile '{profile_name}': {str(e)}")
