import pandas as pd
import pymysql

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
    Load a CSV file into a specific database table.
    
    Args:
        connection: The pymysql connection object.
        csv_file (str): Path to the CSV file.
        table_name (str): Name of the table in the database.
        
    Returns:
        None
    """
    try:
        # Read CSV into DataFrame
        df = pd.read_csv(csv_file)
        print(f"Loaded CSV {csv_file} with {len(df)} rows.")
        
        # Insert DataFrame rows into the table
        with connection.cursor() as cursor:
            for _, row in df.iterrows():
                # Dynamically create SQL INSERT statement
                columns = ", ".join(row.index)
                placeholders = ", ".join(["%s"] * len(row))
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, tuple(row))
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