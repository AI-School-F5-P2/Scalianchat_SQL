# Script to handle Azure SQL Database
import pyodbc
import pandas as pd
import load_env_var
import time
import streamlit as st


def establish_db_connection_retry():
    max_retries = 10
    retry_delay = 5
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Load environment variables
            db_server, db_name, db_user, db_pass, db_port, db_driver = load_env_var.load_env_variables_db()

            # Create connection string
            conn_str = f'DRIVER={{{db_driver}}};SERVER={db_server},{db_port};DATABASE={db_name};UID={db_user};PWD={db_pass};CONNECTION TIMEOUT=30'

            # Connect to the Azure database
            conn = pyodbc.connect(conn_str)
            print('Connection to database successfully established.')
            return conn
        except Exception as e:
            print(f"Error creating connection to database: {e}")
            #st.markdown(f"Por favor, espere. Estableciendo conexión con la BD ({retry_count + 1}/{max_retries})")
            retry_count += 1
            time.sleep(retry_delay)

    st.error("No se pudo establecer la conexión con la base de datos. Por favor, recargue la página.")
    return None



def establish_db_connection():
    """
    This function establishes a connection to the Azure database
    Return: pyodbc.Connection object
    """
    try:
        # Load environment variables
        db_server, db_name, db_user, db_pass, db_port, db_driver = load_env_var.load_env_variables_db()

        # Create connection string
        conn_str = f'DRIVER={{{db_driver}}};SERVER={db_server},{db_port};DATABASE={db_name};UID={db_user};PWD={db_pass};CONNECTION TIMEOUT=30'

        # Connect to the Azure database
        conn = pyodbc.connect(conn_str)

        print('Connection to database successfully established.')

        return conn

    except Exception as e:
        print(f"Error creating connection to database: {e}")


def create_table(connection, table_name):
    """
    This function creates a table in the database if it doesn't exist
    Params:
    -connection: pyodbc.Connection object returned by establish_db_connection function
    -table_name: name of the table to be created
    Return: None
    """
    try:
        cursor = connection.cursor()
        
        # Create table if it doesn't exist
        create_table_query = f"""
            IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}')
            BEGIN
                CREATE TABLE {table_name} (
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

        # Execute create_table_query
        cursor.execute(create_table_query)

        # Commit the transaction and print success message
        connection.commit()
        print(f'Table {table_name} successfully created.')

    except Exception as e:
        print(f"Error creating {table_name} table: {e}")


def insert_data_from_csv(connection, csv_file, table_name):
    """
    This function inserts data from a csv file into a table in the database
    Params:
    -connection: pyodbc.Connection object returned by establish_db_connection function
    -csv_file: path to the csv file with the data to be inserted
    -table_name: name of the table where data is going to be inserted
    Return: None
    """
    try:
        # Load the csv file into a pandas DataFrame
        df = pd.read_csv(csv_file)

        # Create a cursor object using the connection
        cursor = connection.cursor()

        # Query to insert data into the table
        insert_query = f"""
            INSERT INTO {table_name} 
            (entity_name, city, state_abbreviation, variable_name, year, value, unit, definition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Convert the DataFrame to a list of tuples
        data_to_insert = [tuple(row) for row in df.values]

        # Execute the insert query
        cursor.executemany(insert_query, data_to_insert)

        # Commit the transaction and print success message
        connection.commit()
        print(f'Data successfully inserted in table {table_name}.')
    
    except Exception as e:
        print(f'Error loading data: {str(e)}')


def get_schema_representation_any_table(connection):
    """
    This function returns a dictionary with the schema representation for the financial_data table
    Params:
    -connection: pyodbc.Connection object returned by establish_db_connection function
    Return: schema representation for the table in a JSON-like format
    """
    cursor = connection.cursor()

    # Query to get all table names
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")
    tables = cursor.fetchall()

    db_schema = {}

    for table in tables:
        table_name = table[0]

        # Query to get column details for each table
        cursor.execute(
            f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';")
        columns = cursor.fetchall()

        column_details = {}
        for column in columns:
            column_name = column[0]
            column_type = column[1]
            column_details[column_name] = column_type

        db_schema[table_name] = column_details

    return db_schema


def get_schema_representation(connection, table_name):
    """
    This function returns a dictionary with the schema representation for the specified table
    Params:
    -connection: pyodbc.Connection object obtained from establish_db_connection function
    -target_table: name of the table to retrieve schema information
    Return: dictionary representing the schema of the specified table
    """
    cursor = connection.cursor()
    db_schema = {}

    # Query to get column details for the specified table
    cursor.execute(
        f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}';")
    columns = cursor.fetchall()

    column_details = {}
    for column in columns:
        column_name = column[0]
        column_type = column[1]
        column_details[column_name] = column_type

    db_schema[table_name] = column_details
    
    return db_schema


if __name__ == "__main__":
    
    csv_path = 'data/datos_actualizados.csv' # CSV file path
    
    table_name = 'financial_data' # Table where data is going to be inserted

    conn = establish_db_connection()
    
    create_table(conn, table_name)  # Create table if it doesn't exist
    
    insert_data_from_csv(conn, csv_path, table_name)  # Insert data from csv files
    
    conn.close()  # Close the database connection







