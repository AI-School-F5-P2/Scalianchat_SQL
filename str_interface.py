import time
import streamlit as st
import plotly
import openai
import base64
from streamlit_float import *
import plotly.graph_objects as go
from rag_openai import get_completion_from_messages, generate_plot, chart_intention, get_explanation_for_speech
import pandas as pd
from prompts.prompts_sql import SYSTEM_MESSAGE_SQL
from prompts.prompts_chart import SYSTEM_MESSAGE_CHART
from prompts.prompts_intention import SYSTEM_MESSAGE_CHART_INTENTION
from prompts.prompts_explanation import SYSTEM_MESSAGE_SPEECH
from azure_db import establish_db_connection, get_schema_representation, establish_db_connection_retry
from interface_utils import get_text_from_speech, get_speech_from_text
from interface_utils import get_sql_code_from_response, get_plotly_code_from_response
from load_env_var import load_env_variables_openai

# --------------------------------------------
# Azure OpenAI environment variables
# --------------------------------------------

openai.api_type, openai.api_base, openai.api_version, openai.api_key, llm_model, emb_model = load_env_variables_openai()



# --------------------------------------------
# Streamlit App
# --------------------------------------------

about_text = """
**App para generar consultas SQL y gráficos a partir de lenguaje natural basados en la entrada del usuario.**

**Equipo de Desarrollo:**
- [Ana Milena Gómez Giraldo (Scrum Master)](https://www.linkedin.com/in/ana-milena-gomez-giraldo/)
- [Karla Lamus](https://www.linkedin.com/in/karla-lamus/)
- [Miguel Mendoza](https://www.linkedin.com/in/miguelmendozaespinoza)
- [Sandra Gómez Santamaría (Product Owner)](https://www.linkedin.com/in/sandragomezs/)

[Repositorio GitHub](https://github.com/AI-School-F5-P2/Scalianchat_SQL.git)
"""

# Streamlit settings
st.set_page_config(
    page_title="Scalian SQL Chatbot",
    page_icon="images/fav_eva.png",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items = {
        'About': about_text
    }
)


def gif(file_gif):
    """
    This function returns the base64 representation of a gif file
    Params:
    -file_gif: path to the gif file.
    Returns:
    -base64 representation of the gif file.
    """
    file = open(file_gif, "rb")
    contents = file.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file.close()
    return data_url

eva = gif("images/eva_01.gif")


# Display the app title and description
col11, col21, col31 = st.columns([.1, .1, .1])
with col21:
    st.image("images/scalian-spain.png", width=450)
    st.write("")
    st.write("")
    st.write("")

col12, col22, col32 = st.columns([.20, .8, .10])
with col12:
    st.markdown(f'<img src="data:image/gif;base64,{eva}" alt="Eva" width="120">', unsafe_allow_html=True)
with col22:
    st.markdown("#### Hola, soy Eva, tu asistente virtual")
    st.markdown("###### Mi misión es ayudarte a generar consultas SQL y visualizar los resultados.")
    st.write("")

# Create footer container for the microphone
    footer_container = st.container()
    with footer_container:
        st.session_state.micro = st.toggle(":studio_microphone:", key="toggle", help="Encender/Apagar el micrófono")
   

def add_questions(question):
    """
    This function adds a question to the list of last questions.
    Params:
    -question: Question to add to the list (type question: str)
    """
    st.session_state.last_questions.append({"question": question})
    
    # Keep the list of the last 3 questions only
    if len(st.session_state.last_questions) > 3:
        st.session_state.last_questions.pop(0)

    return st.session_state.last_questions


if "openai_model" not in st.session_state:
    st.session_state["assistant"] = llm_model

# Initialize memory for questions and responses
if "last_questions" not in st.session_state:
    st.session_state.last_questions = []

# Initialize chat history for interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Soy un chatbot diseñado para ayudarte a "
                                  "traducir lenguaje natural a consultas "
                                  "SQL válidas. También puedo generar gráficos "
                                  "y soy multilingüe, ¡así que "
                                  "siéntete libre de escribir en el idioma que prefieras!"}]


# Initialize the toggle state
if 'micro' not in st.session_state:
    st.session_state.micro = False

speech_explanation = False


# --------------------------------------------
# Database Connection
# --------------------------------------------

with st.spinner("Estableciendo conexión con la base de datos, por favor espere..."):
    conn = establish_db_connection_retry()
    time.sleep(0)

# Initialize variables
table_name = 'financial_data'
chart_prefix = "[CHART_CODE]"

# Schema representation for the table specified previously
schemas = get_schema_representation(conn, table_name)


# --------------------------------------------
# Display chat messages from history on APP RERUN
# --------------------------------------------

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


# --------------------------------------------
# USER INPUT AND ANSWERS
# --------------------------------------------
          
if user_message := st.chat_input("Escribe aquí tu consulta.") or st.session_state.micro:
    
    if st.session_state.micro:
        user_message =  get_text_from_speech()
        speech_explanation = True

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

    # Call the LLM model to generate the SQL query
    with st.chat_message("assistant"):
        
        st.markdown("###### Answer:")
        try:
            response = get_completion_from_messages(formatted_system_message, user_message)
            st.write(response)
        except Exception as e:
            st.write(f"Lo siento, en estos momentos estamos muy solicitados. Espere un minuto y vuelva a intentarlo.")

        try:
            sql_code = get_sql_code_from_response(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

                # Run the SQL query and display the results
            try:
                sql_results = pd.read_sql_query(sql_code, conn)
                st.markdown("###### Query Results:")
                st.dataframe(sql_results)

                # Save the dataframe and the explanation into the history chat for the interface
                st.session_state.messages.append({"role": "assistant", "content": sql_results})

                # Determine if the user is asking for a chart
                try:
                    intention = chart_intention(SYSTEM_MESSAGE_CHART_INTENTION, user_message)
                except Exception as e:
                    st.write(f"Lo siento, en estos momentos estamos muy solicitados. "
                             f"Espere un minuto y vuelva a intentarlo.")

                if intention == "True":

                    formatted_system_message_chart = SYSTEM_MESSAGE_CHART.format(df=sql_results, sql_code=sql_code)

                    try:
                        response_chart = generate_plot(formatted_system_message_chart, user_message)
                    except Exception as e:
                        st.write(f"Lo siento, en estos momentos estamos muy solicitados. "
                                 f"Espere un minuto y vuelva a intentarlo.")

                    try:
                        code_plot = get_plotly_code_from_response(response_chart)

                        st.markdown("###### Generated Chart:")

                        exec(code_plot)

                        st.plotly_chart(fig, use_container_width=True)

                        # Save the image into the history chat
                        st.session_state.messages.append({"role": "assistant", "content": f"{chart_prefix} {code_plot}"})

                    except Exception as e:
                        st.write(f"Response: {response_chart} - {e}")

                if speech_explanation:
                    system_message_speech = SYSTEM_MESSAGE_SPEECH.format(sql_code=sql_code, df=sql_results)

                    try:
                        response = get_explanation_for_speech(system_message_speech, user_message)
                    except Exception as e:
                        st.write(f"Lo siento, en estos momentos estamos muy solicitados. "
                                 f"Espere un minuto y vuelva a intentarlo.")
                    get_speech_from_text(response)
                    speech_explanation = False

            except Exception as e:
                st.write(f"*La consulta SQL es inválida, división por cero o la pregunta está fuera de contexto.")

        except Exception as e:
            st.write(e)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Pantalla Ana
# footer_container.float("bottom:1rem; right:-8rem; position:fixed;")
# Pantalla SGS Laptop
footer_container.float("bottom:1rem; right:1rem; position:fixed;")
#Pantalla SGS Grande
#footer_container.float("bottom:1rem; right:12rem; position:fixed;")