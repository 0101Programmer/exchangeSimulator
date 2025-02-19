import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
database_url = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(database_url)