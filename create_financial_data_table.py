import pyodbc
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Obtain path variables values from environment variables
db_server = os.getenv('AZURE_DB_SERVER')
db_name = os.getenv('AZURE_DB_NAME')
db_user = os.getenv('AZURE_DB_USER')
db_pass = os.getenv('AZURE_DB_PASS')
db_port = os.getenv('AZURE_DB_PORT')
db_driver = os.getenv('DB_DRIVER')

# Create connection string
conn_str = f"DRIVER={{db_driver}};SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_pass}"



try:
    # Create connection object
    conn = pyodbc.connect(conn_str)
    # Create cursor object
    cursor = conn.cursor()

    # Create table financial_data if it doesn't exist
    create_table_query = """
        IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'financial_data')
        BEGIN
            CREATE TABLE financial_data (
                id int NOT NULL PRIMARY KEY IDENTITY(1,1), 
                entity_name varchar(255),
                city varchar(255),
                state_abbreviation varchar(255),
                variable_name varchar(255),
                year int,
                value float,
                unit varchar(13),
                definition varchar(MAX)
            );
        END
        """

    # Execute creation table query
    cursor.execute(create_table_query)

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    print("Table financial_data created successfully")

except Exception as e:
    print(f"Error creating connection to database: {e}")
