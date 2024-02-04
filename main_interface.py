import streamlit as st
import pandas as pd
from prompts.prompts import SYSTEM_MESSAGE
from azure_openai import get_completion_from_messages
from azure_db import establish_db_connection, get_schema_representation
import json


conn = establish_db_connection()

table_name = 'financial_data'

# Schema representation for the table specified previously
schemas = get_schema_representation(conn, table_name)

st.title("SQL Query Generator with GPT-3.5 Turbo")
st.write("Enter your message to generate SQL and view results:")

# Input field for the user to type a message
user_message = st.text_input("Enter your message:")

if user_message:
    # Format the system message with the schema
    formatted_system_message = SYSTEM_MESSAGE.format(schema=schemas[table_name])
    print(formatted_system_message)

    # Use GPT-3.5-turbo to generate the SQL query
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
        sql_results = pd.read_sql_query(query, conn)
        st.write("Query Results:")
        st.dataframe(sql_results)

    except Exception as e:
        st.write(f"An error occurred: {e}")
