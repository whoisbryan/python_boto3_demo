import pytest
from moto import mock_aws
import boto3
from python_boto3_demo.rds_utils.remove_public_access import check_public_access, remove_public_access  # Ajusta según tu estructura

@mock_aws
def test_check_public_access_with_no_instances():
    """
    Verifica que la función `check_public_access` retorna una lista vacía cuando no hay instancias RDS.
    """
    rds_client = boto3.client('rds', region_name='us-east-1')
    result = check_public_access()
    assert result == []


@mock_aws
def test_check_public_access_with_public_instance():
    """
    Verifica que la función `check_public_access` identifica correctamente las instancias públicas.
    """
    rds_client = boto3.client('rds', region_name='us-east-1')

    rds_client.create_db_instance(
        DBInstanceIdentifier='public-instance',
        AllocatedStorage=20,
        DBInstanceClass='db.t2.micro',
        Engine='mysql',
        MasterUsername='admin',
        MasterUserPassword='password',
        PubliclyAccessible=True
    )

    result = check_public_access()
    assert result == ['public-instance']


@mock_aws
def test_check_public_access_with_private_instance():
    """
    Verifica que la función `check_public_access` no incluya instancias privadas en la lista.
    """
    rds_client = boto3.client('rds', region_name='us-east-1')

    rds_client.create_db_instance(
        DBInstanceIdentifier='private-instance',
        AllocatedStorage=20,
        DBInstanceClass='db.t2.micro',
        Engine='mysql',
        MasterUsername='admin',
        MasterUserPassword='password',
        PubliclyAccessible=False
    )

    result = check_public_access()
    assert result == []


@mock_aws
def test_remove_public_access():
    """
    Verifica que la función `remove_public_access` actualice correctamente el acceso público de una instancia.
    """
    rds_client = boto3.client('rds', region_name='us-east-1')

    rds_client.create_db_instance(
        DBInstanceIdentifier='public-instance',
        AllocatedStorage=20,
        DBInstanceClass='db.t2.micro',
        Engine='mysql',
        MasterUsername='admin',
        MasterUserPassword='password',
        PubliclyAccessible=True
    )

    remove_public_access('public-instance')

    response = rds_client.describe_db_instances(DBInstanceIdentifier='public-instance')
    instance = response['DBInstances'][0]

    assert instance['PubliclyAccessible'] is False
