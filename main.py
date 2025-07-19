import os
import dotenv
import tools as T
import helper as H
import constant as C
import database as DB
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.exceptions import OutputParserException
from openai import AuthenticationError, RateLimitError, APIError, Timeout
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

dotenv.load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
# Prompt template

def StartProject():
    global C  # optional, if you need to reassign C.DB_Schema

    # ========== Initialize Tools ==========
    C.TOOLS.append(T.ConnectToDB)
    C.TOOLS.append(T.ExecuteSQL)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "{system_message}"),
        ("user", "{human_message}")
    ])

    # ========== Prepare messages ==========
    messages = prompt.format(
        system_message=C.SYSTEM_MESSAGE[0],
        human_message=C.HUMAN_MESSAGE[0]
    )

    # ========== Initialize LLM ==========
    llm = init_chat_model(model=C.OPENAI_MODEL, model_provider=C.MODEL_PROVIDER)
    # llm = G.init_gemini()

    # ========== Create Connection Agent ==========
    dbConnectAgent = T.InitializeAgent(C.TOOLS, llm)

    # ========== Ask Agent to Connect to DB ==========
    response = dbConnectAgent.invoke(messages)
    if response is None:
        raise Exception("🔴 Agent returned None as response.")
    else:
        print("✅ Agent response:", response)

    # Extract connection status from output
    output = response.get("output", "")
    connection_status = output.split('\n')[0]
    if connection_status == False:
        print("🔴 Database connection failed as per agent response.")
        exit(1)

    # ========== Initialize DB ==========
    db = DB.GetDBConnection()
    if db is None:
        raise Exception("🔴 DB returned None even though agent said connection was successful.")

    # ========== Initialize Toolkit ==========
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    C.TOOLS.extend(toolkit.get_tools())

    # ========== Create Schema Agent ==========
    schemaAgent = T.InitializeAgent(C.TOOLS, llm)

    # ========== Ask for schema summary ==========
    messages = prompt.format(
        system_message=C.SYSTEM_MESSAGE[1],
        human_message=C.HUMAN_MESSAGE[1]
    )

    schema_response = schemaAgent.invoke(messages)
    C.DB_SCHEMA = schema_response['output']  # ✅ update global
    print("✅ Schema summary saved..!")

    user_query = input("[0 to exit], Enter your question: ")
    if user_query == "0":
        exit(0)

    while user_query != "0":
        # ========== Ask for user query ==========
        messages = prompt.format(
            system_message=C.SYSTEM_MESSAGE[2],
            human_message=C.HUMAN_MESSAGE[2].format(schema=C.DB_SCHEMA, user_question=user_query)
        )

        user_query_response = schemaAgent.invoke(messages)
        print("✅ User Query Response:\n", user_query_response['output'])
        user_permission = input("Execute Query ? (y/n): ")

        if user_permission == "y":
            # ========== Execute Query ==========
            messages = prompt.format(
                system_message=C.SYSTEM_MESSAGE[3],
                human_message=C.HUMAN_MESSAGE[3].format(sql_query=user_query_response['output'])
            )

            ExecuteAgent = T.InitializeAgent(C.TOOLS, llm)
            execute_response = ExecuteAgent.invoke(messages)
            print("✅ Execute Response:\n", execute_response['output'])

        user_query = input("[0 to exit], Enter your question: ")

    print("Goodbye!")


def main():
    print("Starting....!")
    StartProject()


if __name__ == "__main__":
    main()
