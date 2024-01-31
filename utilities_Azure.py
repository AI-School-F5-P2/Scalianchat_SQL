import pyodbc
import pandas as pd
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
conn_str = f"DRIVER={{{db_driver}}};SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_pass}"

# Ruta al archivo CSV
csv_path = 'data/datos_Actualizados.csv'

# Nombre de la tabla
table_name = 'financial_data'


def insert_data_from_csv(cursor, csv_path, table_name):
    try:
        # Lee el CSV en un DataFrame
        df = pd.read_csv(csv_path)

        # Crea un cursor
        cursor = conn.cursor()

        # Prepara la consulta SQL con parámetros de inserción masiva
        insert_query = f"""
            INSERT INTO {table_name} 
            (entity_name, city, state_abbreviation, variable_name, year, value, unit, definition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Convierte el DataFrame a una lista de tuplas
        data_to_insert = [tuple(row) for row in df.values]

        # Ejecuta la consulta de inserción masiva
        cursor.executemany(insert_query, data_to_insert)

        # Confirma la transacción
        conn.commit()

        print(f'Datos cargados exitosamente en la tabla {table_name}.')
    except Exception as e:
        print(f'Error al cargar datos: {str(e)}')

# Ejemplo de uso
if __name__ == "__main__":
    # Establecer conexión a la base de datos
    conn = pyodbc.connect(conn_str)



    # Llamar a la función
    insert_data_from_csv(conn, csv_path, table_name)

    # Cerrar la conexión después de su uso
    conn.close()
