import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()


def load_env_variables_db():
    db_server = os.getenv('AZURE_DB_SERVER')
    db_name = os.getenv('AZURE_DB_NAME')
    db_user = os.getenv('AZURE_DB_USER')
    db_pass = os.getenv('AZURE_DB_PASS')
    db_port = os.getenv('AZURE_DB_PORT')
    db_driver = os.getenv('DB_DRIVER')
    return db_server, db_name, db_user, db_pass, db_port, db_driver


def load_env_variables_openai():
    openai.api_type = "azure"
    openai.api_base = os.getenv("AZURE_OPENAI_API_BASE")
    openai.api_version = os.getenv('AZURE_API_VERSION')
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
    return openai.api_base, openai.api_version, openai.api_key

