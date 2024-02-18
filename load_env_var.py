import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Database environment variables
def load_env_variables_db():
    db_server = os.getenv('AZURE_DB_SERVER')
    db_name = os.getenv('AZURE_DB_NAME')
    db_user = os.getenv('AZURE_DB_USER')
    db_pass = os.getenv('AZURE_DB_PASS')
    db_port = os.getenv('AZURE_DB_PORT')
    db_driver = os.getenv('DB_DRIVER')
    return db_server, db_name, db_user, db_pass, db_port, db_driver


# AzureOpenAI environment variables
def load_env_variables_openai():
    openai.api_type = "azure"
    openai.api_base = os.getenv('AZURE_OPENAI_API_BASE')
    openai.api_version = os.getenv('AZURE_API_VERSION')
    openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')
    llm_model = os.getenv('AZURE_OPENAI_LLM_MODEL')
    emb_model = os.getenv('AZURE_OPENAI_EMBEDDING_MODEL')
    return openai.api_type, openai.api_base, openai.api_version, openai.api_key, llm_model, emb_model


# AzureOpenAI environment variables: different model implementations to distribute the load (requests to the API)
def load_env_variables_models():
    chart_model = os.getenv('AZURE_OPENAI_MODEL_CHART')
    return chart_model


# AzureSearch environment variables
def load_env_variables_azure_search():
    search_endpoint = os.getenv('SEARCH_ENDPOINT')
    search_key = os.getenv('SEARCH_ADMIN_KEY')
    search_index_name = os.getenv('SEARCH_INDEX_NAME')
    return search_endpoint, search_key, search_index_name


# AzureSpeech environment variables
def load_env_variables_azure_speech():
    speech_api_key = os.getenv('SPEECH_API_KEY')
    return speech_api_key