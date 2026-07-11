# 🗄️ SQL AI Assistant

An interactive **Streamlit + LangChain** app that lets you query your **SQLite** or **MySQL** database using natural language, powered by **Groq LLMs**.

## 🚀 Live Demo

🔗 https://sql-ai-assistant-97mbomabkzknlsomc6gcph.streamlit.app/

> 💡 When deployed on Streamlit Cloud, MySQL must be hosted on a publicly accessible server. Localhost databases are supported only when running the app locally.

---

## 🖼️ Screenshots
<img width="1917" height="863" alt="image" src="https://github.com/user-attachments/assets/0f352225-5a9d-4794-84e8-8737bdf31d18" />
<img width="1918" height="862" alt="image" src="https://github.com/user-attachments/assets/67fb070a-97d0-491f-8b1f-cb2ea5fb1c95" />
<img width="1918" height="857" alt="image" src="https://github.com/user-attachments/assets/5b03247c-eebf-4d52-8e2b-f4696978d84f" />
<img width="1918" height="865" alt="image" src="https://github.com/user-attachments/assets/b0eb16ab-b221-41a4-8117-b807cb2b6fdc" />
<img width="1918" height="862" alt="image" src="https://github.com/user-attachments/assets/32faafb8-925d-4fc8-b69d-05c5971ffa05" />

---

## ✨ Features

- 💬 Ask SQL questions in plain English
- 🧠 Uses LangChain SQL Agent for query generation/execution
- 🗃️ Supports:
  - Local **SQLite** database (read-only mode)
  - Remote/Public **MySQL** database
- 🔐 Groq API key input from UI (session-only)
- 🤖 Select from multiple Groq models (or provide custom model name)
- 🧵 Multiple chat histories via **Conversation ID**
- ♻️ Reset conversation from sidebar
- ⚡ Built with Streamlit for quick deployment

---

## 📁 Project Structure

```text
sql-ai-assistant/
├── streamlit.py
├── requirements.txt
├── student.db
└── README.md
```

---

## 🧰 Tech Stack

- [Streamlit](https://streamlit.io/)
- [LangChain](https://www.langchain.com/)
- [LangChain Community](https://python.langchain.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Groq + langchain_groq](https://groq.com/)
- [mysql-connector-python](https://pypi.org/project/mysql-connector-python/)

---

## 📦 Installation

### 1) Clone the repository

```bash
git clone https://github.com/Shuvadip-Dutta/sql-ai-assistant.git
cd sql-ai-assistant
```

### 2) Create and activate a virtual environment (recommended)

**Windows (PowerShell):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
streamlit run streamlit.py
```

Then open the local URL shown in terminal (usually `http://localhost:8501`).

---

## 🔑 Configuration

When the app opens, use the sidebar to configure:

1. **Groq API Key** (required)
2. **Model** (preset or custom)
3. **Database Type**
   - **SQLite** (loads local `student.db`)
   - **MySQL** (requires host, port, user, password, DB name)

---

## 🗃️ Database Support

### SQLite
- Uses the bundled `student.db`
- Opened in **read-only** mode for safety

### MySQL
Provide:
- Host
- Port (default `3306`)
- Username
- Password
- Database name

---

## 💡 How It Works

- App creates a LangChain SQL agent using:
  - `create_sql_agent`
  - `SQLDatabase`
  - `ChatGroq`
- Agent inspects schema and answers based only on database contents
- Chat messages are stored in `st.session_state` by `conversation_id`

---

## ✅ Example Prompts

- “Show all tables in the database.”
- “What columns exist in the students table?”
- “How many students scored above 90?”
- “List top 5 students by marks.”
- “What is the average score per class?”

---

## ⚠️ Notes & Limitations

- Ensure your selected Groq model is valid and available for your API key.
- MySQL connection may fail if host is not reachable.
- Responses depend on actual schema/data quality.
- Keep API keys secure; avoid sharing screenshots with secrets.

---

## 🛠️ Troubleshooting

### App stops with “Please enter your Groq API key”
Add your Groq API key in the sidebar first.

### MySQL connection fails
Check:
- Host/port accessibility
- Credentials
- Database name
- Firewall/network restrictions

### Module import errors
Reinstall dependencies:
```bash
pip install -r requirements.txt
```

---

## 📌 Requirements

Current `requirements.txt` includes:

- `langchain`
- `python-dotenv`
- `langchain-community`
- `langchain-classic`
- `streamlit`
- `langchain_groq`
- `langchain_core`
- `mysql-connector-python`
- `SQLAlchemy`

---

## 📄 License

Add your preferred license (MIT, Apache-2.0, etc.) in a `LICENSE` file.

---

## 👨‍💻 Author

**Shuvadip Dutta**  
GitHub: [@Shuvadip-Dutta](https://github.com/Shuvadip-Dutta)
