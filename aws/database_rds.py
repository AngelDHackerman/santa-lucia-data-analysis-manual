import boto3
import json
from botocore.exceptions import ClientError

rds_client = boto3.client('rds')

# Get the secret from AWS Secrets Manager
def get_secret():

    secret_name = "LotteryDBCredentials"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Parse the secret string into a dictionary
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret['username'], secret['password']


# Create client for RDS
def create_rds_instance(db_instance_identifier, db_name):
    # Get credentials from Secrets Manager
    master_username, master_password = get_secret()
    try:
        response = rds_client.create_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            AllocatedStorage=20, # size in GB (20 for the free tier)
            DBInstanceClass='db.t3.micro', # free tier instance class
            Engine='mysql', # Database motor
            MasterUsername=master_username,
            MasterUserPassword=master_password,
            DBName=db_name,
            BackupRetentionPeriod=7, # Backup retention period
            PubliclyAccessible=True # Public access enabled
        )
        print(f"RDS instance {db_instance_identifier} created successfully.")
        return response
    except Exception as e:
        print(f"Error creating RDS instance: {e}")
        
# Setup
db_instance_identifier = "Lottery-db-instance"
db_name = "Lottery_db"


create_rds_instance(db_instance_identifier, db_name)