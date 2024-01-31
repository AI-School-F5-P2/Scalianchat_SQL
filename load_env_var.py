import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_env_variables():
    db_server = os.getenv('AZURE_DB_SERVER')
    db_name = os.getenv('AZURE_DB_NAME')
    db_user = os.getenv('AZURE_DB_USER')
    db_pass = os.getenv('AZURE_DB_PASS')
    db_port = os.getenv('AZURE_DB_PORT')
    db_driver = os.getenv('DB_DRIVER')
    return db_server, db_name, db_user, db_pass, db_port, db_driver

