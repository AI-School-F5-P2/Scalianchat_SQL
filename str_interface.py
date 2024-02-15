import streamlit as st
import plotly
import plotly.graph_objects as go
from rag_openai import get_completion_from_messages, generate_plot
import pandas as pd
from prompts.prompts_sql import SYSTEM_MESSAGE_SQL
from prompts.prompts_chart import SYSTEM_MESSAGE_CHART
import json
from azure_db import establish_db_connection, get_schema_representation

# Establish a connection to the database
conn = establish_db_connection()

# Initialize variables
table_name = 'financial_data'
dataframe_code_block = ""
chart_code = ""
grafico_prefix = "[GRAFICO_CODE]"

# Schema representation for the table specified previously
schemas = get_schema_representation(conn, table_name)


def add_questions(question):
    """
    This function adds a question to the list of last questions
    Params:
    -question: Question to add to the list (type question: str)
    """
    st.session_state.last_questions.append({"question": question})
    
    # Keep the list of the last 3 questions only
    if len(st.session_state.last_questions) > 3:
        st.session_state.last_questions.pop(0)

    return st.session_state.last_questions


# --------------------------------------------
# Streamlit app
# --------------------------------------------

# Streamed response interface
st.title("SChatGPT-like clone")


if "openai_model" not in st.session_state:
    st.session_state["assistant"] = 'gpt4-0613'

# Initialize memory for questions and responses
if "last_questions" not in st.session_state:
    st.session_state.last_questions = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Mi nombre es Eve, soy tu asistente virtual. "
                                                                  "¿En qué puedo ayudarte?"}]


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        
        # Check if the content of the message is graph code
        if isinstance(message["content"], str) and message["content"].startswith(grafico_prefix):
            
            # If it's graph code, execute it to obtain the fig object.
            code_plot = message["content"][len(grafico_prefix):].strip()
            exec(code_plot, globals())
            fig = go.Figure()
            
            # Check if the fig object was created successfully
            if 'fig' in globals() and isinstance(fig, plotly.graph_objs._figure.Figure):
                # If the fig object is a valid plot, display it
                st.plotly_chart(fig)
            
            else:
                # If the fig object was not created successfully, display an error message
                st.error("Error generating chart.")
        
        else:
            # If it's not chart code, display the message content as text.
            st.write(message["content"])


# Accept user input
if user_message := st.chat_input("Enter your message to generate SQL and view results."):
    user_message = user_message.lower()
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Add user message to last questions
    st.session_state.last_questions = add_questions(user_message)
    
    #Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_message.title())

    print(st.session_state.last_questions)

    formatted_system_message = SYSTEM_MESSAGE_SQL.format(table_name=table_name, schema=schemas[table_name],
                                                         last_questions=st.session_state.last_questions)

    print(f"formatted_system_message: {formatted_system_message}")

    # Call the LLM model to generate the SQL query
    with st.chat_message("assistant"):
        
        response = get_completion_from_messages(formatted_system_message, user_message)

        try:
            #Convert the response to a dictionary
            response = eval(response)

            print(f'The response is: {response} and the type is: {type(response)}')
            
            query = response["sql_code"]
            print(f'query: {query}')
            ask_for_chart = response["ask_for_chart"]
            print(f'chart_code: {chart_code}')
            explanation = response["sql_code_explanation"]
            print(f'explanation: {explanation}')

            # Display the generated SQL query
            st.write("Generated SQL Query:")
            st.code(query, language="sql")

            # Convert the SQL query to a block format to save it into the history chat for interface
            sql_code_block = f"```sql\n{query}\n```"
            st.session_state.messages.append({"role": "assistant", "content": sql_code_block})

            try:
                # Run the SQL query and display the results
                sql_results = pd.read_sql_query(query, conn)
                st.write("Query Results:")
                st.dataframe(sql_results)
                st.write(explanation)

                # Save the dataframe and the explanation into the history chat for the interface
                st.session_state.messages.append({"role": "assistant", "content": sql_results})
                st.session_state.messages.append({"role": "assistant", "content": explanation})

                if ask_for_chart:
                    df = sql_results
                    formatted_system_message_chart = SYSTEM_MESSAGE_CHART.format(table_name=table_name, schema=schemas[table_name])
                    
                    response_chart = generate_plot(formatted_system_message_chart, df)
                            
                    try:
                        response_chart_json = json.loads(response_chart)
                        code_plot = response_chart_json.get('code_chart', None)

                        # Process only the chart code, removing the header
                        code_plot_lines = code_plot.split('\n')
                        start_index = code_plot_lines.index("```python") + 1
                        end_index = code_plot_lines.index("```", start_index)
                        code_plot_clean = '\n'.join(code_plot_lines[start_index:end_index])

                        st.write("Generated Chart:")
                        exec(code_plot_clean, globals())
                        
                        if 'fig' in globals():
                            st.plotly_chart(fig, use_container_width=True)

                            grafico_prefix = "[GRAFICO_CODE]"

                            # save the image into the history chat
                            st.session_state.messages.append({"role": "assistant", "content": f"{grafico_prefix} {code_plot_clean}"})
                            
                        else:
                            print("The generated chart code did not define 'fig' variable.")
                            
                    except json.JSONDecodeError as e:
                        st.write(f"Response: {response_chart} - {e}")
                
            except json.JSONDecodeError as e:
                st.write(f"An error occurred while connecting to database: {e}")

        except SyntaxError as e:
            print(f'{e} and its type is {type(e)}')
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})