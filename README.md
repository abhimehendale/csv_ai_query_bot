🤖 CSV/Excel AI Query Bot

An AI-powered assistant that lets you query CSV or Excel files in plain English.
No coding required — just type your question, and the bot automatically writes and executes Pandas/Matplotlib code to return answers or generate charts.

Built with Python + OpenAI API + Pandas + Matplotlib.

🚀 Features

📂 Upload CSV or Excel files and explore them instantly

📝 Natural language queries → converted into Python code automatically

🔡 Case-insensitive column handling → all columns normalized to snake_case

✨ Two intelligent modes:

Text-only → returns summaries, calculations, tables in terminal
Chart mode → generates and saves one matplotlib chart per request

🖼 Unique chart saving → every chart saved with timestamped filenames (charts/plot_2025MMDD_HHMMSS.png)

🔒 Safe execution → sandboxed code execution with restricted environment

⚡ Plug-and-play with your OpenAI API key via .env

🛠 Tech Stack

Python 3.9+
Pandas – data analysis
Matplotlib – visualizations
OpenAI API – AI code generation
Dotenv – environment variables

📂 Project Structure

    csv_ai_query_bot/
    │
    ├── main.py             # Core script (CLI assistant)
    ├── requirements.txt    # Dependencies
    ├── datasets/           # Sample CSV/Excel files
    ├── charts/             # Auto-generated charts (created at runtime)
    ├── .env                # API key (not committed)
    └── README.md           # Documentation


⚡ Quickstart
1️⃣ Clone the repo
    git clone https://github.com/YOUR_USERNAME/csv_ai_query_bot.git
    cd csv_ai_query_bot

2️⃣ Create a virtual environment
    python -m venv .venv
    source .venv/bin/activate   # Mac/Linux
    # .venv\Scripts\activate    # Windows

3️⃣ Install dependencies
    pip install -r requirements.txt

4️⃣ Add your API key to .env
    OPENAI_API_KEY=your_api_key_here

5️⃣ Run the bot
    python main.py

🎯 Usage Examples
Text-only queries (no chart)
    - Which salesperson sold how many total units?
    - Average revenue by region
Chart queries
    - Plot units_sold by salesperson as a bar chart
    - Give me a line chart of revenue by month

📌 Future Enhancements

🌐 Streamlit web interface for interactive data exploration
🔍 SQL-style querying for CSVs
📊 Export results to Excel/PDF


💡 Why this project matters

- Shows hands-on AI + Python + Data Analysis skills
- Demonstrates ability to build real-world AI assistants for businesses
- Valuable for freelancing (AI automation / data analysis gigs) and as a portfolio project   to land AI/ML roles


⚡ This project is a showcase of turning AI + automation + data analysis into a practical tool.
