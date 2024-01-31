# Script to handle Azure SQL Database

import pyodbc
import pandas as pd
# from dotenv import load_dotenv
# import os
import load_env_var

# Ruta al archivo CSV
csv_path = 'data/datos_Actualizados.csv'

# Nombre de la tabla
table_name = 'financial_data'

# Load environment variables
db_driver, db_server, db_name, db_user, db_pass = load_env_var.load_env_variables()

# Create connection string
conn_str = f"DRIVER={{{db_driver}}};SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_pass}"
# Establecer conexión a la base de datos
conn = pyodbc.connect(conn_str)


def create_table(connection):
    """
    This function creates a table in the database if it doesn't exist
    :param connection:
    :return:
    """
    try:
        cursor = connection.cursor()
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
        # conn.close()
        print("Table financial_data created successfully")

    except Exception as e:
        print(f"Error creating connection to database: {e}")


def insert_data_from_csv(connection, csv_file, table):
    """
    This function inserts data from a csv file into a table in the database
    :param connection:
    :param csv_file:
    :param table:
    :return:
    """
    try:
        # Lee el CSV en un DataFrame
        df = pd.read_csv(csv_file)

        # Crea un cursor
        cursor = connection.cursor()

        # Prepara la consulta SQL con parámetros de inserción masiva
        insert_query = f"""
            INSERT INTO {table} 
            (entity_name, city, state_abbreviation, variable_name, year, value, unit, definition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Convierte el DataFrame a una lista de tuplas
        data_to_insert = [tuple(row) for row in df.values]

        # Ejecuta la consulta de inserción masiva
        cursor.executemany(insert_query, data_to_insert)

        # Confirma la transacción
        connection.commit()

        print(f'Datos cargados exitosamente en la tabla {table_name}.')
    except Exception as e:
        print(f'Error al cargar datos: {str(e)}')


create_table(conn)  # Create table financial_data if it doesn't exist
insert_data_from_csv(conn, csv_path, table_name)  # Insert data from csv files
conn.close()  # close the connection


