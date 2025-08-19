# 🤖 CSV/Excel AI Assistant (Streamlit)

A web-based version of the CSV/Excel AI Query Bot. Upload CSV/Excel, ask questions in natural language, and see answers/charts inline.

## Features
- Upload CSV/Excel

- Natural language queries → pandas/matplotlib code (generated via OpenAI Responses API)

- Text-only mode vs Chart mode (auto-inferred from your question)

- Normalized lowercase snake_case column names for robust querying

- Safe execution sandbox

- Optional saving of charts to `/charts` with timestamped filenames

## Run locally

```bash

pip install -r requirements.txt

export OPENAI_API_KEY=YOUR_KEY

streamlit run streamlit_app.py


Tips

If you don’t mention words like “chart/plot/graph”, the app will return a text answer only.

Column names are normalized, so “Revenue”, “revenue”, and “REVENUE” all work.