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

# Create tables
def create_tables():
    username, password, host, database_name  = get_secret()
    
    connection = pymysql.connect(
        host=host,
        user=username,
        password=password,
        database=database_name
    )
    try:
        with connection.cursor() as cursor:
            # Create header table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Header (
                numero_sorteo INT PRIMARY KEY,
                tipo_sorteo VARCHAR(50),
                fecha_sorteo DATE,
                fecha_caducidad DATE,
                primer_premio INT,
                segundo_premio INT,
                tercer_premio INT,
                reintegro_primer_premio INT,
                reintegro_segundo_premio INT,
                reintegro_tercer_premio INT
            );                 
            """)
            
            # Create body table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Body (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero_sorteo INT,
                numero_premiado INT,
                letras VARCHAR(5),
                monto DECIMAL(10, 2),
                vendido_por VARCHAR(255),
                FOREIGN KEY (numero_sorteo) REFERENCES Header(numero_sorteo)
            );
            """)
            
            connection.commit()
            print("Tables created successfully")
    finally:
        connection.close()
        
# Execute function
create_tables()