import csv
import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
import tiktoken

csv_file_path = 'data/datos_actualizados.csv'


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


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
                sql="COPY financial_data(\"entity_name\", \"city\", \"state_abbreviation\", \"variable_name\", \"year\", \"value\", \"unit\", \"definition\") FROM STDIN WITH CSV HEADER DELIMITER ','",
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
        "id" SERIAL PRIMARY KEY NOT NULL,
        "entity_name" VARCHAR(255),
        "city" VARCHAR(255),
        "state_abbreviation" VARCHAR(255),
        "variable_name" VARCHAR(255),
        "year" INTEGER,
        "value" FLOAT,
        "unit" VARCHAR(13),
        "definition" VARCHAR(1000000)
    )
    """)


    # Insert data from csv files
    #insert_data_from_csv(cursor, 'financial_data', csv_file_path)

print(num_tokens_from_string("¿Qué institución financiera tenía los activos totales más altos en el año 2020?", "cl100k_base"))


# Commit the transaction and close the connection
conn.commit()
conn.close()






