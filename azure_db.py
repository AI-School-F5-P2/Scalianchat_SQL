# Script to handle Azure SQL Database
import pyodbc
import pandas as pd
import load_env_var

# CSV file path
csv_path = 'data/datos_Actualizados.csv'

# Table where data is going to be inserted
table_name = 'financial_data'

# Load environment variables
db_server, db_name, db_user, db_pass, db_port, db_driver = load_env_var.load_env_variables_db()

# Create connection string
conn_str = f"DRIVER={{{db_driver}}};SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_pass}"

# Connect to the database
conn = pyodbc.connect(conn_str)


def create_table(connection, table_name):
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

        # Commit the transaction
        conn.commit()
        print(f'Table {table_name} successfully created')

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

        print(f'Data successfully inserted in table {table_name}.')
    
    except Exception as e:
        print(f'Error loading data: {str(e)}')


def get_schema_representation_any_table(connection):
    """
    This function returns a dictionary with the schema representation for the financial_data table
    :param connection:
    :return:
    """
    """ Get the database schema in a JSON-like format """
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

def get_schema_representation(connection, target_table):
    """
    This function returns a dictionary with the schema representation for the specified table
    :param connection: pyodbc.Connection object
    :param target_table: Name of the table to retrieve schema information
    :return: Dictionary representing the schema of the specified table
    """
    cursor = connection.cursor()
    db_schema = {}

    # Query to get column details for the specified table
    cursor.execute(
        f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{target_table}';")
    columns = cursor.fetchall()

    column_details = {}
    for column in columns:
        column_name = column[0]
        column_type = column[1]
        column_details[column_name] = column_type

    db_schema[table_name] = column_details
    return db_schema






# This code will only run when the file is executed directly
if __name__ == "__main__":
    create_table(conn, table_name)  # Create table if it doesn't exist
    insert_data_from_csv(conn, csv_path, table_name)  # Insert data from csv files
    conn.close()  # close the connection







