import os
import constant as C
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from langchain_community.utilities import SQLDatabase

# Load environment variables
def GetDBConnection():
    db_user = C.DB_USER
    db_host = C.DB_HOST
    db_port = C.DB_PORT
    db_name = C.DB_NAME
    db_password = C.DB_PASSWORD

    # Build connection string
    # By default, LangChain's SQLDatabase looks only in the public schema.
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    try:
        # Create engine
        engine = create_engine(DATABASE_URL)

        # ✅ Test DB connection with SELECT 1
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")

    except SQLAlchemyError as e:
        print("❌ Database connection failed:", e)
        return None

    # ✅ LangChain SQL wrapper
    db = SQLDatabase(
        engine=engine,
        include_tables=None,                   # Include all tables
        sample_rows_in_table_info=0,           # Disable sampling
        schema="shop"
    )
    return db