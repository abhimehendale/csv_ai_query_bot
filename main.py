import pandas as pd
from tabulate import tabulate
import os
from openai import OpenAI
from dotenv import load_dotenv

# ==== CONFIG ====
# Make sure you set your API key as an environment variable:
# export OPENAI_API_KEY="your_api_key"   (Mac/Linux)
# setx OPENAI_API_KEY "your_api_key"     (Windows)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_file(file_path):
    """Load CSV or Excel file into a Pandas DataFrame."""
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Only CSV or Excel files are supported.")

def generate_pandas_code(question, df_head):
    """Ask the AI to generate Pandas code for the given question."""
    prompt = f"""
You are a Python data analysis assistant.
I have a dataframe named df with the following columns:
{', '.join(df_head.columns)}

Sample of data:
{df_head.to_string(index=False)}

Write ONLY the Pandas code (without explanations) to answer the following question.
Do NOT include variable assignments except for the result (if needed).
Question: "{question}"
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

def execute_code(code, df):
    """Execute generated Pandas code safely."""
    # Remove any code block markers like ```python ... ```
    code = code.replace("```python", "").replace("```", "").strip()

    local_vars = {"df": df, "pd": pd}
    try:
        # Ensure we can capture the output in a variable
        if not code.strip().startswith("result"):
            code = f"result = {code}"
        exec(code, {}, local_vars)
        return local_vars["result"]
    except Exception as e:
        return f"Error executing code: {e}"

def main():
    print("=== CSV/Excel AI Query Bot ===")
    file_path = input("Enter the path to your CSV/Excel file: ").strip()
    df = load_file(file_path)
    print("\nData Preview:")
    print(tabulate(df.head(), headers="keys", tablefmt="pretty"))

    while True:
        question = input("\nAsk a question (or type 'exit' to quit): ").strip()
        if question.lower() == "exit":
            break

        code = generate_pandas_code(question, df.head())
        #print(f"\n[Generated Code]:\n{code}\n")
        result = execute_code(code, df)

        if isinstance(result, pd.DataFrame):
            print(tabulate(result.head(), headers="keys", tablefmt="pretty"))
        else:
            print(result)

if __name__ == "__main__":
    main()
