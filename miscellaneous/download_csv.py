import pymysql
import pandas as pd
import boto3
import json
from botocore.exceptions import ClientError

# Get aws credentials
def get_secret():
    secret_name = "LotteryDBCredentials"
    region_name = "us-east-1"
    
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    return secret['username'], secret['password'], secret['host'], secret['db_name']

# connect to the database
def connect_to_db():
    username, password, host, db_name = get_secret()
    connection = pymysql.connect(host=host, user=username, password=password, database=db_name)
    return connection

# download data as CSV
def export_table_to_csv(table_name, output_csv):
    connection = connect_to_db()
    try:
        query = f"SELECT * FROM {table_name}" # Select all data in the table
        df = pd.read_sql(query, connection) # Execute the query and save the dataframe
        df.to_csv(output_csv, index=False) # Exports to a csv file
        print(f"Data exported correctly to {output_csv}")
    except Exception as e:
        print(f"Error exporting data: {e}")
    finally:
        connection.close()
        
if __name__ == "__main__":
    export_table_to_csv("Sorteos", "./sorteos_export.csv")
    export_table_to_csv("Premios", "./premios_export.csv")
    export_table_to_csv("calendar_sorteos", "./calendar_export.csv")
    export_table_to_csv("letter_combinations", "./combinatios_export.csv")