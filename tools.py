import constant as C
from sqlalchemy import text
from typing import Optional
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, AgentType

@tool
def ConnectToDB(dummy_input: Optional[str] = None) -> str:
    """Use this tool if connection to the database is needed"""
    db = C.DB
    if db:
        return "✅ Database connection successful!\n"
    else:
        return "❌ Database connection failed!\n"



@tool
def ExecuteSQL(query: str) -> str:
    """
    Executes a SQL query directly. Returns rows if SELECT, or summary if data is changed.
    Commits changes for INSERT/UPDATE/DELETE/DDL.
    """
    try:
        db = C.DB  # returns SQLDatabase
        engine = db._engine  # actual SQLAlchemy engine

        with engine.begin() as conn:  # 🔄 begin = commit-enabled transaction
            print("Query: ", query)
            result = conn.execute(text(query))
            if query.strip().lower().startswith("select"):
                rows = result.fetchall()
                return f"✅ Fetched rows:\n{[dict(row._mapping) for row in rows]}"
            else:
                return f"✅ Query executed. Rows affected: {result.rowcount}"


        # Commit changes if applicable
        if query.strip().lower().startswith(("insert", "update", "delete", "drop", "create")):
            conn.commit()
        
        conn.close()

    except Exception as e:
        return f"🔴 Error executing query: {str(e)}"

# Store globally (or pass via a state manager)
prompt = ChatPromptTemplate.from_messages([
    ("system", "{system_message}"),
    ("user", "{human_message}")
])

@tool
def RefreshSchema() -> str:
    """
    Refreshes the global DB_Schema by invoking the schema summary agent again.
    This should be called after any query that changes the schema (ALTER, CREATE, DROP).
    """

    try:
        messages = prompt.format(
            system_message=C.SYSTEM_MESSAGE[1],
            human_message=C.HUMAN_MESSAGE[1]
        )

        response = C.SchemaAgent.invoke(messages)
        C.DB_Schema = response['output']

        return "✅ DB schema refreshed successfully."
    except Exception as e:
        return f"🔴 Failed to refresh schema: {str(e)}"


def InitializeAgent(tools, llm):
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        max_iterations=2,  # ⛔️ prevent infinite loops
        verbose=True,
        early_stopping_method="generate",
        handle_parsing_errors=True
    )
    return agent
