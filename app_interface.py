import streamlit as st
import pandas as pd
from azure_db import establish_db_connection, get_schema_representation
from prompts.prompts import SYSTEM_MESSAGE
import json
import matplotlib
import matplotlib.pyplot as plt
import plotly.graph_objects as go
matplotlib.use('Agg')
from charts_utils import save_chart_code_to_temp_file
from rag_openai import get_completion_from_audio, get_completion_from_messages

# Establish a connection to the database
conn = establish_db_connection()

# Table name
table_name = 'financial_data'

# Schema representation for the table specified previously
schemas = get_schema_representation(conn, table_name)

# Streamlit introduction
st.title("SQL Query Generator with GPT-3.5 Turbo")
with st.chat_message("assistant"):
    st.write("This app uses OpenAI's GPT-3.5-turbo to generate SQL queries and visualizations from natural language messages.")
    st.write("You can ask questions about the financial data table and the model will generate the SQL query and visualization code.")
    st.write("For example, you can ask questions like:")
    st.write("- What bank had the highest total assets in 2020?")
    st.write("- What is the lowest value of total securities for all banks in Texas?")
    st.write("- Generate chart")

user_message = st.chat_input("Enter your message to generate SQL and view results.")

if user_message:
    # Format the system message with the schema
    user_message = user_message.lower()
    formatted_system_message = SYSTEM_MESSAGE.format(table_name=table_name, schema=schemas[table_name])
    
    #Use GPT-4 to generate the SQL query
    response = get_completion_from_messages(formatted_system_message, user_message)

    if response:
        try:
            json_response = json.loads(response)
            print(f"json_response: {json_response}")
            query = json_response.get('query', None)
            print(f"query: {query}")
            chart_code = json_response.get('chart', None)
            print(f"chart_code: {chart_code}")
            error = json_response.get('error', None)
            print(f"error: {error}")

            if query:
                # Display the generated SQL query
                st.write("Generated SQL Query:")
                st.code(query, language="sql")

                try:
                    # Run the SQL query and display the results
                    sql_results = pd.read_sql_query(query, conn)
                    st.write("Query Results:")
                    st.dataframe(sql_results)

                    if chart_code:
                        # Save the chart code to a temporary file
                        temp_file_name = save_chart_code_to_temp_file(chart_code)

                        # Import the chart code and display the chart
                        st.write("Generated Chart:")
                        exec(open(temp_file_name).read())

                        # Guarda el gráfico como una imagen
                        fig = go.Figure()
                        st.plotly_chart(fig, use_container_width=True)
                        #plt.savefig('temp_plot.png')

                        # Muestra la imagen en Streamlit
                        st.image('temp_plot.png')
                
                except Exception as e:
                    with st.chat_message("assistant"):
                        st.write(f"An error occurred while running the SQL query: {e}")

            elif error:
                with st.chat_message("assistant"):
                    st.write(f"An error occurred: {error}")

        except json.JSONDecodeError as e:
            with st.chat_message("assistant"):
                st.write(f"An error occurred while decoding the response: {e}")
                st.write(f"Response: {response}")