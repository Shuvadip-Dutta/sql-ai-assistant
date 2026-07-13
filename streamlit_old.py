import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits import create_sql_agent
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

st.title("🗄️ SQL AI Assistant")
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
    "deepseek-r1-distill-llama-70b",
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
        return SQLDatabase(create_engine(f"sqlite:///",creator=creator))
        
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
        return SQLDatabase(engine=engine)    

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

    agent = create_sql_agent(
        llm=llm,
        db=db,
        handle_parsing_errors=True,
        verbose=False,
        prefix="""
        You are an expert SQL assistant.
        When answering:
        - First understand the database schema.
        - Use only information present in the database.
        - Never invent tables, columns, or values.
        - Explain findings in plain English.
        - If the user asks what is in the database, summarize the tables and their columns.
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
        messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                response = agent.invoke({"input": user_input})

                messages.append(
                    {
                        "role": "assistant",
                        "content": response["output"]
                    }
                )

                st.markdown(response["output"])

else:
    st.info("👈 Connect to a database using the sidebar to start chatting.")