import csv
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

csv_file_path = 'data/datos_actualizados.csv'
#absolute_path = os.path.abspath(csv_file_path)
#print(absolute_path)

def insert_data_from_csv(cursor, table_name,csv_file_path):
    """
    This function inserts data from a csv file into a table
    """
    try:
        # Open the csv file
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Skip the first line (headers)
            next(file)
            cursor.copy_expert(
                sql="COPY financial_data(\"ENTITY_NAME\", \"CITY\", \"STATE_ABBREVIATION\", \"VARIABLE_NAME\", "
                    "\"YEAR\", \"VALUE\", \"UNIT\", \"DEFINITION\") FROM STDIN WITH CSV HEADER DELIMITER ','",
                file=file)
    except Exception as e:
        print(f"Error insertando datos en la tabla {table_name} desde archivo CSV {csv_file_path}: {e}")
        # Rollback the transaction to avoid partial data insertion
        conn.rollback()
    else:
        # Commit the transaction if there were no errors
        conn.commit()



# Load environment variables
load_dotenv()

# configuration for database connection
connection_params = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'port': os.getenv('DB_PORT')
}

# Stablish a connection to the database

conn = psycopg2.connect(**connection_params)

# Create a cursor to execute SQL commands
cur = conn.cursor()

# Execute the SQL command to create the table
with cur as cursor:
    cursor.execute("""CREATE  TABLE IF NOT EXISTS financial_data (
        "ID" SERIAL PRIMARY KEY NOT NULL,
        "ENTITY_NAME" VARCHAR(255),
        "CITY" VARCHAR(255),
        "STATE_ABBREVIATION" VARCHAR(255),
        "VARIABLE_NAME" VARCHAR(255),
        "YEAR" INTEGER,
        "VALUE" FLOAT,
        "UNIT" VARCHAR(13),
        "DEFINITION" VARCHAR(1000000)
    )
    """)


    # Insert data from csv files
    insert_data_from_csv(cursor, 'financial_data', csv_file_path)


# Commit the transaction and close the connection
conn.commit()
conn.close()






