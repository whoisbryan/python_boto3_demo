import pytest
import json
from moto import mock_aws
import boto3
from python_boto3_demo.ec2_utils.remove_ssm_policy import get_instance_profiles, check_and_remove_ssm_policy

SSM_POLICY_ARN = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"

@mock_aws
def test_get_instance_profiles_with_no_instances():
    """
    Verifica que la función `get_instance_profiles` retorne una lista vacía si no hay instancias EC2.
    """
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    result = get_instance_profiles()
    assert result == []


@mock_aws
def test_get_instance_profiles_with_instances():
    """
    Verifica que `get_instance_profiles` detecte correctamente instancias con perfiles IAM.
    """
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    iam_client = boto3.client('iam', region_name='us-east-1')


    iam_client.create_role(
        RoleName="test-role",
        AssumeRolePolicyDocument='{"Version": "2012-10-17", "Statement": []}'
    )
    iam_client.create_instance_profile(InstanceProfileName="test-profile")
    iam_client.add_role_to_instance_profile(InstanceProfileName="test-profile", RoleName="test-role")


    ec2_client.run_instances(
        ImageId="ami-12345678",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        IamInstanceProfile={"Name": "test-profile"}
    )

    result = get_instance_profiles()
    assert len(result) == 1
    assert result[0][1] == "test-profile"



@mock_aws
def test_check_and_remove_ssm_policy():
    iam_client = boto3.client('iam', region_name='us-east-1')

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "ssm:*",
                "Resource": "*"
            }
        ]
    }
    
    policy = iam_client.create_policy(
        PolicyName="CustomSSMManagedInstanceCore",
        PolicyDocument=json.dumps(policy_document),
        Description="Simulated SSM policy for testing purposes",
        Path="/",
    )
    
    custom_policy_arn = policy['Policy']['Arn']

    iam_client.create_role(
        RoleName="test-role",
        AssumeRolePolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole"
                }
            ]
        })
    )

    iam_client.attach_role_policy(
        RoleName="test-role",
        PolicyArn=custom_policy_arn
    )

    iam_client.create_instance_profile(InstanceProfileName="test-profile")
    iam_client.add_role_to_instance_profile(InstanceProfileName="test-profile", RoleName="test-role")
    attached_policies = iam_client.list_attached_role_policies(RoleName="test-role")['AttachedPolicies']
    assert any(policy['PolicyArn'] == custom_policy_arn for policy in attached_policies)



@mock_aws
def test_check_and_remove_ssm_policy_no_policy():
    """
    Verifica que `check_and_remove_ssm_policy` no genere errores si no hay políticas SSM adjuntas.
    """
    iam_client = boto3.client('iam', region_name='us-east-1')

    iam_client.create_role(
        RoleName="test-role",
        AssumeRolePolicyDocument='{"Version": "2012-10-17", "Statement": []}'
    )
    iam_client.create_instance_profile(InstanceProfileName="test-profile")
    iam_client.add_role_to_instance_profile(InstanceProfileName="test-profile", RoleName="test-role")

    check_and_remove_ssm_policy("test-profile")

    attached_policies = iam_client.list_attached_role_policies(RoleName="test-role")['AttachedPolicies']
    assert len(attached_policies) == 0
