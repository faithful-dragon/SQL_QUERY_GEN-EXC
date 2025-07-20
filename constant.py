import os
import dotenv
import helper as H
import database as D
dotenv.load_dotenv()


DRIVER_NAME = os.getenv("DRIVER_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
SCHEMA_NAME = "library"
SchemaAgent = None
DB_SCHEMA = ''

OPENAI_MODEL = "gpt-4o-mini"
MODEL_PROVIDER = "openai"

SYSTEM_MESSAGE = H.SystemMessage()
HUMAN_MESSAGE = H.HumanMesssage()
TOOLS = []

DB = D.GetDBConnection()