import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from llm import ask_model_for_code
from safe_exec import run_generated_code, normalize_columns

load_dotenv()

st.set_page_config(page_title="CSV/Excel AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 CSV/Excel AI Assistant (Web)")
st.caption(
    "Upload a CSV/Excel, ask a question in plain English. "
    "The app generates pandas/matplotlib code, runs it safely, and shows the answer below."
)

# ---- Sidebar settings ----
with st.sidebar:
    st.header("Settings")
    model = st.text_input("OpenAI model", os.getenv("MODEL", "gpt-4o-mini"))
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.1)
    max_tokens = st.slider("Max tokens", 256, 2048, 700, 32)
    save_chart_files = st.checkbox("Save charts to /charts with timestamped names", value=False)

uploaded = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded is None:
    st.info("Upload a CSV/Excel file to begin.")
    st.stop()

# Read file
if uploaded.name.lower().endswith(".csv"):
    df = pd.read_csv(uploaded)
else:
    df = pd.read_excel(uploaded)

# Normalize columns to lowercase snake_case (so queries are case-insensitive)
df = normalize_columns(df)

st.subheader("Preview")
st.dataframe(df.head(50), use_container_width=True)
st.info("Columns: " + ", ".join(df.columns))

# ---- Query box ----
question = st.text_input(
    "Ask a question (e.g., 'which salesperson sold how many total units?' or 'plot revenue by region as a bar chart')"
).strip()

# Infer whether a chart is expected
want_chart = False
if question:
    ql = question.lower()
    for k in ["chart", "plot", "graph", "bar chart", "line chart", "scatter", "histogram"]:
        if k in ql:
            want_chart = True
            break

go = st.button("Generate answer", type="primary")

if not go:
    st.stop()

if not question:
    st.warning("Please type a question.")
    st.stop()

# ---- Generate code from the model ----
with st.spinner("Generating code..."):
    # pass a small sample to give the model context without sending the whole file
    df_sample = df.sample(min(len(df), 200)).to_dict(orient="records")
    code = ask_model_for_code(
        question=question,
        df_sample=df_sample,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        want_chart=want_chart,
    )

st.subheader("Generated Code")
st.code(code, language="python")

# ---- Execute code safely and display results ----
with st.spinner("Running the code safely..."):
    result = run_generated_code(code, df, want_chart=want_chart, save_files=save_chart_files)

if result.get("error"):
    st.error(result["error"])

if result.get("text"):
    st.subheader("Answer")
    st.write(result["text"])

if result.get("dataframe") is not None:
    st.subheader("Table")
    st.dataframe(result["dataframe"], use_container_width=True)

if result.get("figure") is not None:
    st.subheader("Chart")
    st.pyplot(result["figure"])

if result.get("saved_path"):
    st.success(f"Chart saved to: `{result['saved_path']}`")
