# Este script es para postgresql.
# No se va autilizar para el desarrollo en Azure  

from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain import SQLDatabase
from langchain_openai import OpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents import create_sql_agent as create_agent
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# configuration for database connection

host= os.getenv('DB_HOST')
database= os.getenv('DB_NAME')
user= os.getenv('DB_USER')
password= os.getenv('DB_PASS')
port= os.getenv('DB_PORT')


# Stablish a connection to the database

# Create SQLDatabase object from the connection
db = SQLDatabase.from_uri(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}')

# choose llm model, in this case the default OpenAI model
llm = OpenAI(
            temperature=0,
            verbose=True,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            )

# setup agent

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    actions=[{"action": "sql_db_schema", "params": {"table": "financial_data"}}]
    )


# Add the sql_db_schema action to retrieve information about the table structure
#agent_executor.add_action("sql_db_schema", {"table": "financial_data"})

# define the user's question
#question = "¿Qué institución financiera tenía los activos totales más altos en el año 2020?"
question = "¿Qué instituciones financieras de California tuvieron el mayor valor de activos totales entre 2010 y 2015?"
#question = "¿Cuál fue el valor % asegurado (estimado) más alto de todas las instituciones financieras del estado de Nueva Jersey?"
agent_executor.invoke(question)