import pandas as pd
import pymysql
import json
import boto3
from botocore.exceptions import ClientError
import re

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

def connect_to_db(user, password, host, database, port=3306):
    """
    Establish a connection to the database.
    
    Args:
        user (str): Database user.
        password (str): Database password.
        host (str): Database host.
        database (str): Database name.
        port (int): Database port (default is 3306).
        
    Returns:
        connection: A pymysql connection object.
    """
    
    try:        
        connection = pymysql.connect(
            user=user,
            password=password,
            host=host,
            database=database,
            port=port
        )
        print("Database connection established.")
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to database: {e}")
        raise
    
def load_csv_to_table(connection, csv_file, table_name):
    """
    Load a CSV file into a specific database table using batched inserts.
    """
    # validate table name 
    if not re.match(r"^[a-zA-Z0-9_]+$", table_name):
        raise ValueError("Invalid table name. Only alphanumeric characters and underscores are allowed.")
    
    try:
        # Read CSV into DataFrame
        df = pd.read_csv(csv_file)
        print(f"Loaded CSV {csv_file} with {len(df)} rows.")
        
        # Generate SQL and batch insert
        columns = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Convert DataFrame to list of tuples for efficient insertion
        data = [tuple(row) for row in df.to_numpy()]
        
        with connection.cursor() as cursor:
            cursor.executemany(sql, data)  # Batch insert, optimizes performance when working with large volumes of data.
        connection.commit()
        print(f"Data from {csv_file} loaded into table {table_name}.")
    except Exception as e:
        print(f"Error loading CSV {csv_file} into table {table_name}: {e}")
        connection.rollback()
        raise

    
def close_db_connection(connection):
    """
    Close the database connection.
    
    Args:
        connection: The pymysql connection object.
        
    Returns:
        None
    """
    if connection:
        connection.close()
        print("Database connection closed.")
        
def start_upload_csv_file(csv_file, table_name):
    """
    Orchestrates the complete upload process of the CSV to the database.
    """
    try:
        # Get the credentials for the AWS Data base
        username, password, host, db_name = get_secret()
        
        # Connect to the Data base
        connection = connect_to_db(username, password, host, db_name)
        
        # Load CSV to table
        load_csv_to_table(connection, csv_file, table_name)
    
    finally:
        close_db_connection(connection)
    