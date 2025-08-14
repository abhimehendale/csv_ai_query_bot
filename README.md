# CSV/Excel AI Query Bot

A Python-based AI-powered bot that lets you query CSV or Excel files using natural language.  
It converts your questions into Pandas code, executes them, and returns results — no coding required!

## 🚀 Features
- Load **CSV** or **Excel** files
- Ask questions in plain English
- AI converts your question into **Pandas** code
- Returns **data tables** as output
- Supports `.env` for storing your **OpenAI API key**

## 🛠 Tech Stack
- Python
- Pandas
- OpenAI API
- Tabulate

## 📂 Project Structure

csv_ai_query_bot/
│
├── main.py # Core script
├── requirements.txt # Dependencies
├── .gitignore # Ignore venv and sensitive files
├── .env # Environment variables (DO NOT COMMIT)
├── datasets/ # Sample CSV/Excel files
└── README.md # Documentation

## 📦 Setup Instructions

### 1️⃣ Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/csv_ai_query_bot.git
cd csv_ai_query_bot

2️⃣ Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
# .venv\Scripts\activate    # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Add your OpenAI API key to .env
Create a .env file in the root folder:
|
|-- OPENAI_API_KEY=your_api_key_here

5️⃣ Run the bot
python main.py

📌 Future Enhancements

Add chart/graph generation

Build a Streamlit web interface

Support SQL queries from CSV data