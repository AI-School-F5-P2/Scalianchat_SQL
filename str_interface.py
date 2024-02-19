import streamlit as st
import plotly
import plotly.graph_objects as go
from rag_openai import get_completion_from_messages, generate_plot, chart_intention
import pandas as pd
from prompts.prompts_sql import SYSTEM_MESSAGE_SQL
from prompts.prompts_chart import SYSTEM_MESSAGE_CHART
from prompts.prompts_intention import SYSTEM_MESSAGE_CHART_INTENTION
import json
from azure_db import establish_db_connection, get_schema_representation
from interface_utils import get_sql_code_from_response, get_plotly_code_from_response

# Establish a connection to the database
conn = establish_db_connection()

# Initialize variables
table_name = 'financial_data'
chart_prefix = "[CHART_CODE]"

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
# Streamlit App
# --------------------------------------------

# Streamed response interface
st.title("SChatGPT-like clone")


if "openai_model" not in st.session_state:
    st.session_state["assistant"] = 'gpt4-0613'

# Initialize memory for questions and responses
if "last_questions" not in st.session_state:
    st.session_state.last_questions = []

# Initialize chat history for interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Mi nombre es Eve, soy tu asistente virtual. "
                                                                  "¿En qué puedo ayudarte?"}]


# Display chat messages from history on APP RERUN
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        
        # Check if the content of the message is chart code
        if isinstance(message["content"], str) and message["content"].startswith(chart_prefix):
            
            # If it's graph code, execute it to obtain the fig object.
            code_plot = message["content"][len(chart_prefix):].strip()
            fig = go.Figure()
            exec(code_plot)
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            # If it is not chart code, display the message content as text.
            st.write(message["content"])


# Accept user input
if user_message := st.chat_input("Enter your message to generate SQL and view results."):
    
    # Add user message to chat history interface
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Add user message to last questions
    st.session_state.last_questions = add_questions(user_message)
    
    #Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_message)
    
    user_message = user_message.lower()

    formatted_system_message = SYSTEM_MESSAGE_SQL.format(table_name=table_name, schema=schemas[table_name],
                                                         last_questions=st.session_state.last_questions)

    print(f"System message for SQL code: {formatted_system_message}")

    # Call the LLM model to generate the SQL query
    with st.chat_message("assistant"):
        
        st.markdown("###### Answer:")
        
        response = get_completion_from_messages(formatted_system_message, user_message)
        
        st.write(response)

        try:
            sql_code = get_sql_code_from_response(response)

            st.session_state.messages.append({"role": "assistant", "content": response})

            try:
                # Run the SQL query and display the results
                sql_results = pd.read_sql_query(sql_code, conn)
                st.markdown("###### Query Results:")
                st.dataframe(sql_results)

                # Save the dataframe and the explanation into the history chat for the interface
                st.session_state.messages.append({"role": "assistant", "content": sql_results})

                # Determine if the user is asking for a chart
                intention = chart_intention(SYSTEM_MESSAGE_CHART_INTENTION, user_message)
                print(f'The intention is: {intention} with type {type(intention)}')

                if intention == "True":
                    
                    formatted_system_message_chart = SYSTEM_MESSAGE_CHART.format(df=sql_results, sql_code=sql_code)
                    
                    print(formatted_system_message_chart)

                    response_chart = generate_plot(formatted_system_message_chart, user_message)         
                    
                    try:
                        code_plot = get_plotly_code_from_response(response_chart)

                        print(f'Este es el código: {code_plot}')

                        st.markdown("###### Generated Chart:")
                        
                        exec(code_plot)
                        
                        st.plotly_chart(fig, use_container_width=True)

                        # Save the image into the history chat
                        st.session_state.messages.append({"role": "assistant", "content": f"{chart_prefix} {code_plot}"})
                                                                                                               
                    except Exception as e:
                        st.write(f"Response: {response_chart} - {e}")
                
            except  Exception as e:
                st.write(f"*La consulta SQL es inválida o la pregunta está fuera de contexto.")

        except Exception as e:
            st.write(e)
            st.session_state.messages.append({"role": "assistant", "content": response})