from modules.ETL.extract import extract_lottery_data
from modules.ETL.transformer import read_files, split_header_body, process_header, process_body, transform
from modules.ETL.loader import connect_to_db, load_csv_to_table, close_db_connection


# Run the transformer and generate CSV files
sorteos_csv, premios_csv = transform("./miscellaneous")

print(f"Sorteos CSV: {sorteos_csv}")
print(f"Premios CSV: {premios_csv}")







import json
import pymysql
import boto3
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
    return secret['username'], secret['password'], secret['host'], secret['db_name']