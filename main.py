import os
import re
import traceback
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

load_dotenv()

# === Settings ===
DATA_PATH = os.getenv("DATA_PATH", "datasets/sales_data.csv")
MODEL = os.getenv("MODEL", "gpt-4o-mini")

# === Load + normalize dataframe columns (lowercase snake_case) ===
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    def norm(c: str) -> str:
        c = c.strip().lower()
        c = re.sub(r"[^0-9a-z]+", "_", c)  # non-alnum -> underscore
        c = re.sub(r"_+", "_", c).strip("_")
        return c
    df = df.copy()
    df.columns = [norm(c) for c in df.columns]
    return df

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Could not find data file at {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
df = normalize_columns(df)  # e.g., 'Units Sold' -> 'units_sold'

# === OpenAI client ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You write concise, SAFE pandas/matplotlib code to answer a question about a DataFrame named df.
IMPORTANT:
  - All df column names are lowercased snake_case (e.g., 'Units Sold' => 'units_sold').
  - Always refer to columns using these normalized names.
  - If WANT_CHART is False: DO NOT create or show charts. Instead, compute a clear textual answer and assign it to 'answer_text'.
  - If WANT_CHART is True: Create exactly one matplotlib figure assigned to variable 'fig'. Do NOT call plt.show().
  - Do not save charts yourself. Just assign the matplotlib figure to a variable fig.
  - Never read/write files (except through save_chart), never use network calls, never import unsafe modules.
  - Allowed imports: import pandas as pd; import matplotlib.pyplot as plt
  - Keep code under ~80 lines. Avoid printing; set variables instead (answer_text, fig).
OUTPUT:
  - Return ONLY raw Python code (no backticks, no prose).
"""

def ask_ai_for_code(question: str, want_chart: bool) -> str:
    user_payload = {"question": question, "want_chart": want_chart}
    resp = client.responses.create(
        model=MODEL,
        temperature=0.2,
        max_output_tokens=700,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": str(user_payload)},
        ],
    )
    if getattr(resp, "output_text", None):
        return resp.output_text.strip()

    text_chunks = []
    for out in (resp.output or []):
        if getattr(out, "type", None) == "message":
            for c in (getattr(out, "content", None) or []):
                if getattr(c, "type", None) == "output_text" and getattr(c, "text", None):
                    text_chunks.append(c.text)
    return "\n".join(text_chunks).strip()

# ---------- Helpers ----------

def unwrap_code_fences(text: str) -> str:
    if "```" in text:
        parts = text.split("```")
        for i in range(1, len(parts), 2):
            block = parts[i]
            lines = block.splitlines()
            if lines and lines[0].strip().lower().startswith("python"):
                return "\n".join(lines[1:]).strip()
        if len(parts) > 1:
            return parts[1].strip()
    return text.strip()

def normalize_df_name(code: str) -> str:
    code = re.sub(r"\bdffd\b", "df", code)
    code = re.sub(r"\bdfd\b", "df", code)
    code = re.sub(r"\bdff\b", "df", code)
    code = re.sub(r"\bdataframe\b", "df", code, flags=re.IGNORECASE)
    return code

# Unique chart saver provided to the model
def save_chart(fig) -> str:
    os.makedirs("charts", exist_ok=True)
    name = f"plot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    path = os.path.join("charts", name)
    fig.savefig(path, bbox_inches="tight")
    return path

# ---------- Execute model-generated code ----------

def execute_code(code: str, want_chart: bool):
    try:
        clean = unwrap_code_fences(code)
        clean = normalize_df_name(clean)

        banned_snippets = ["subprocess", "os.system(", "open(", "eval(", "exec("]
        for b in banned_snippets:
            if b in clean:
                raise RuntimeError(f"Blocked unsafe usage: {b}")

        local_vars = {
            "df": df,
            "pd": pd,
            "plt": plt,
            "answer_text": None,
            "fig": None,
            "WANT_CHART": want_chart,
        }

        if not want_chart:
            if "plt." in clean or "savefig" in clean:
                raise RuntimeError("Chart not allowed in text-only mode.")

        exec(clean, {}, local_vars)

        if isinstance(local_vars.get("answer_text"), str) and local_vars["answer_text"].strip():
            print(local_vars["answer_text"])

        if want_chart and local_vars.get("fig") is not None:
            try:
                path = save_chart(local_vars["fig"])
                print(f"✅ Chart saved at: {path}")
            except Exception as e:
                print(f"Error saving chart: {e}")

    except Exception as e:
        print(f"Error executing code: {e}")
        traceback.print_exc()

# ---------- CLI ----------

CHART_KEYWORDS = {"chart", "plot", "graph", "bar chart", "line chart", "scatter", "histogram"}

def infer_want_chart(q: str) -> bool:
    ql = q.lower()
    return any(k in ql for k in CHART_KEYWORDS)

def main():
    print("CSV/Excel AI Query Bot (v2: normalized columns, text-only mode, unique charts)")
    print("Type 'exit' to quit.\\n")
    print("Columns available:", ", ".join(df.columns))

    while True:
        q = input("\\n Ask a question: ").strip()
        if not q:
            continue
        if q.lower() in {"exit", "quit"}:
            break

        want_chart = infer_want_chart(q)
        if not want_chart:
            print("[Mode] Text-only")
        else:
            print("[Mode] Chart expected")

        #print("\\n[Generated Code]:")
        code = ask_ai_for_code(q, want_chart)
        #print(code)

        execute_code(code, want_chart)

if __name__ == "__main__":
    main()
