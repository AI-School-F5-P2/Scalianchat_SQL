import streamlit as st
import pandas as pd
import pyodbc
import load_env_var
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
import azure_db
import json

# Load environment variables
db_server, db_name, db_user, db_pass, db_port, db_driver = load_env_var.load_env_variables_db()

# Table name
table_name = 'financial_data'

def query_database(query, conn):
    """ Run SQL query and return results in a dataframe """
    return pd.read_sql_query(query, conn)

# Create a connection string
conn_str = f"DRIVER={{{db_driver}}};SERVER={db_server};DATABASE={db_name};UID={db_user};PWD={db_pass}"

# Stablish connection to the database
conn = pyodbc.connect(conn_str)

# Schema Representation for financial_data table
schemas = azure_db.get_schema_representation(conn, table_name)

st.title("SQL Query Generator with GPT-3.5 Turbo")
st.write("Enter your message to generate SQL and view results.")

# Input field for the user to type a message
user_message = st.text_input("Enter your message:")

if user_message:
    # Format the system message with the schema
    formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas['financial_data'])
    print(formatted_system_message)

    #Use GPT-3.5-turbo to generate the SQL query
    response = get_completion_from_messages(formatted_system_message, user_message)
    print(response)
    json_response = json.loads(response)
    query = json_response['query']
    print(query)

    # Display the generated SQL query
    st.write("Generated SQL Query:")
    st.code(query, language="sql")

    try:
        # Run the SQL query and display the results
        sql_results = query_database(query, conn)
        st.write("Query Results:")
        st.dataframe(sql_results)

    except Exception as e:
        st.write(f"An error occurred: {e}")
