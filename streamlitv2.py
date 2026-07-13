import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits import create_sql_agent
from langchain_classic.agents.agent_types import AgentType
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(
    page_title="SQL AI Assistant",
    page_icon="🗄️",
    layout="wide"
)
LOCAL_DB="USE_LOCAL_DB"
MYSQL_DB="USE_MYSQL_DB"

st.title("🗄️ SQL AI Assistant V2.0")
st.info(
    "💡 When deployed on Streamlit Cloud, MySQL must be hosted on a publicly accessible server. "
    "Localhost databases are supported only when running the app locally."
)
st.caption(
    "Ask questions about your SQL database using natural language."
)

with st.sidebar:
    st.header("⚙️ Configuration")

    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Enter your Groq API key. It is used only for this session."
    )
    if not groq_api_key:
        st.warning("Please enter your Groq API key to continue.")
        st.stop()

    model_options = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "Custom"
    ]

    selected = st.selectbox("Model", model_options)

    if selected == "Custom":
        model = st.text_input(
            "Enter Groq model name",
            placeholder="meta-llama/..."
        )
    else:
        model = selected
    
    db_type = st.radio(
        "Database",
        [
            "SQLite",
            "MySQL"
        ]
    )
    if db_type == "MySQL":
        db_uri=MYSQL_DB
        mysql_host=st.text_input("MySQL Host", value="localhost")
        mysql_port=st.text_input("MySQL Port", value="3306")
        mysql_user=st.text_input("MySQL User", value="root")
        mysql_password=st.text_input("MySQL Password", value="", type="password")
        mysql_db_name=st.text_input("MySQL Database Name", value="test_db")
        connect_db = st.button("🔌 Connect MySQL Database")
    else:
        db_uri=LOCAL_DB
        connect_db = st.button("📂 Load SQLite Database")


    if not db_uri:
        st.warning("Please select a database option.")
        

    conversation_id = st.text_input(
    "Conversation ID",
    value="default",
    help=
    "Use different IDs to maintain separate chat histories."
    )
    
if "chat_store" not in st.session_state:
    st.session_state.chat_store = {}

if conversation_id not in st.session_state.chat_store:
    st.session_state.chat_store[conversation_id] = [
        {
            "role": "assistant",
            "content": "👋 Ask me anything about your SQL database."
        }
    ]
    

messages = st.session_state.chat_store[conversation_id]

if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

if "db" not in st.session_state:
    st.session_state.db = None

if "db_type" not in st.session_state:
    st.session_state.db_type = None

if "model" not in st.session_state:
    st.session_state.model = None

    
@st.cache_resource
def load_llm(api_key, model_name):
    return ChatGroq(
        api_key=groq_api_key,
        model_name=model
    )


llm = load_llm(groq_api_key, model) 

@st.cache_resource(ttl="1h")
def configure_db(db_uri,mysql_host=None,mysql_port=None,mysql_user=None,mysql_password=None,mysql_db_name=None):
    if db_uri == LOCAL_DB:
        dbfilepath=(Path(__file__).parent / "student.db").absolute()
        creator=lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True)
        return SQLDatabase(create_engine(f"sqlite:///",creator=creator), sample_rows_in_table_info=1)
        
    elif db_uri == MYSQL_DB:
        # Create a MySQL database connection
        if not all([mysql_host, mysql_port, mysql_user, mysql_password, mysql_db_name]):
            st.warning("Please provide all MySQL connection details.")
            st.stop()
        url=URL.create(
            "mysql+mysqlconnector",
            username=mysql_user,
            password=mysql_password,
            host=mysql_host,
            port=int(mysql_port),
            database=mysql_db_name
        )
        engine = create_engine(url)
        return SQLDatabase(engine=engine, sample_rows_in_table_info=1)    

current_config = {
    "db_type": db_type,
    "model": model,
}

if st.session_state.get("current_config") != current_config:
    st.session_state.current_config = current_config

    # Clear previous connection
    st.session_state.db_connected = False
    st.session_state.db = None

if connect_db:

    try:

        if db_uri == MYSQL_DB:
            db = configure_db(
                db_uri,
                mysql_host,
                mysql_port,
                mysql_user,
                mysql_password,
                mysql_db_name
            )
        else:
            db = configure_db(db_uri)

        # Save the database connection
        st.session_state.db = db
        st.session_state.db_connected = True
        st.session_state.db_type = db_type
        st.session_state.model = model

        st.rerun()


    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if st.session_state.db_connected:
    st.success(
        f"✅ Connected | Database: **{st.session_state.db_type}** | "
        f"Model: **{st.session_state.model}**"
    )
if not st.session_state.get("db_connected", False):
    st.info("👈 Connect to a database first.")
    st.stop()

if "db" in st.session_state:

    db = st.session_state.db
    engine = db._engine
    table_count = len(db.get_usable_table_names())
    if table_count <= 20:
        mode = "Full Schema"
    else:
        mode = "Table Selection"
    st.info(
        f"ℹ️ Database contains **{table_count}** tables. "
        f"Using **{mode}** mode for schema understanding."
    )
    tables = sorted(db.get_usable_table_names())
    if mode=="Table Selection":
        
        # Initialize session state
        if "selected_tables" not in st.session_state:
            st.session_state.selected_tables = []

        search = st.text_input(
            "🔍 Search Tables",
            placeholder="Search table...And empty the search box to see all tables.",
        )

        # Filter visible tables
        if search:
            filtered_tables = [
                table for table in tables
                if search.lower() in table.lower()
            ]
        else:
            filtered_tables = tables

        # Current visible selection
        visible_selection = st.multiselect(
            "Select tables for the AI",
            filtered_tables,
            default=[
                table
                for table in st.session_state.selected_tables
                if table in filtered_tables
            ]
        )

        # Keep selections from previous searches
        remaining = [
            table
            for table in st.session_state.selected_tables
            if table not in filtered_tables
        ]

        st.session_state.selected_tables = sorted(
            list(set(remaining + visible_selection))
        )

        st.caption(
            f"Selected {len(st.session_state.selected_tables)} of {len(tables)} tables"
        )
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Apply Table Selection"):

                if not st.session_state.selected_tables:
                    st.warning("Please select at least one table.")
                    st.stop()
                
                st.session_state.filtered_db = SQLDatabase(
                    engine,
                    include_tables=st.session_state.selected_tables,
                    sample_rows_in_table_info=1
                )

                st.success("Table selection applied.")
                st.rerun()

        with col2:
            if st.button("🗑️ Clear Selection"):

                st.session_state.selected_tables = []

                # Remove the filtered database
                st.session_state.pop("filtered_db", None)

                st.success("Selection cleared.")

                st.rerun()
    if mode == "Table Selection":
        db = st.session_state.get("filtered_db")
        with st.expander("Tables exposed to AI"):
            st.write(st.session_state.selected_tables)

        if db is None:
            st.info("👈 Select the tables and click **Apply Table Selection**.")
            st.stop()
    else:
        db = st.session_state.db
        
    agent = create_sql_agent(
        llm=llm,
        db=db,
        handle_parsing_errors=True,
        verbose=False,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        prefix = """
        You are an expert SQL assistant.

        Rules:
        - Understand the database schema before answering.
        - Use only existing tables, columns, and values.
        - Never invent schema, relationships, or data.
        - Explain answers in clear natural language.

        This database is READ-ONLY.
        Never generate or execute:
        INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, REPLACE, RENAME, GRANT, REVOKE.

        Only generate SELECT queries.

        SQL Guidelines:
        - Never use SELECT *.
        - Select only the required columns.
        - Use LIMIT unless the user requests all rows.
        - Use COUNT, SUM, AVG, MIN, MAX when appropriate.
        - Generate efficient SQL.

        Relationship Rules:
        - Never assume tables are related.
        - Join tables only when the schema clearly indicates a valid relationship.
        - Never invent JOIN conditions.
        - If no relationship exists, clearly state that instead of generating SQL.

        Schema Questions:
        If the question is about tables, columns, schema, primary keys, foreign keys, or relationships, answer using the schema whenever possible without executing unnecessary queries.

        If the answer cannot be determined from the database, clearly say so instead of guessing.
        """
    )

    if st.sidebar.button("Reset Conversation"):
        st.session_state.chat_store[conversation_id] = [
            {
                "role": "assistant",
                "content": "👋 Ask me anything about your SQL database."
            }
        ]

    messages = st.session_state.chat_store[conversation_id]

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question about your database...")

    if user_input:
        dangerous_requests = [
            "delete",
            "drop",
            "truncate",
            "update",
            "insert",
            "alter",
            "create table",
            "create database",
            "grant",
            "revoke"
        ]

        if any(word in user_input.lower() for word in dangerous_requests):
            st.warning(
                "⚠️ This assistant is running in read-only mode."
            )
            st.stop()
            
        messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                try:
                    relationship_keywords = [
                        "relation",
                        "relationship",
                        "related",
                        "schema",
                        "structure",
                        "foreign key",
                        "primary key",
                        "tables",
                        "columns"
                    ]
                    
                    if any(word in user_input.lower() for word in relationship_keywords):

                        schema = db.get_table_info()

                        prompt = f"""
                    You are an expert database architect.

                    Database Schema:

                    {schema}

                    Using ONLY the schema above, answer this question:

                    {user_input}

                    If the question is about relationships,
                    explain them in plain English.

                    Do NOT generate SQL.
                    """

                        response = llm.invoke(prompt)

                        answer = response.content

                        st.markdown(answer)

                        messages.append(
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        )

                    else:

                        response = agent.invoke(
                            {"input": user_input}
                        )

                        answer = response["output"]

                        st.markdown(answer)


                    # Try to extract generated SQL
                    sql_query = None

                    if "intermediate_steps" in response:
                        try:
                            sql_query = response["intermediate_steps"][-1].tool_input
                        except:
                            pass

                    # Validate generated SQL
                    dangerous_sql = [
                        "DELETE",
                        "UPDATE",
                        "INSERT",
                        "DROP",
                        "ALTER",
                        "TRUNCATE",
                        "CREATE",
                        "GRANT",
                        "REVOKE"
                    ]

                    if sql_query:

                        if any(keyword in sql_query.upper() for keyword in dangerous_sql):
                            st.error("❌ Unsafe SQL detected. Execution blocked.")
                            st.stop()

                        if "SELECT *" in sql_query.upper():
                            st.warning(
                                "⚠️ Generated SQL uses SELECT *. "
                                "Consider selecting only the required columns."
                            )

                        with st.expander("📝 Generated SQL"):
                            st.code(sql_query, language="sql")

                    messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )
                except Exception as e:
                    st.error(str(e))
                    # st.error(
                    #     "The request could not be completed. "
                    #     "Try selecting fewer tables or asking a more specific question."
                    # )

else:
    st.info("👈 Connect to a database using the sidebar to start chatting.")