import os, json
from openai import OpenAI

SYSTEM_PROMPT = """
You are a senior data analyst who writes concise, safe Python code using pandas and matplotlib.

Contract:
- The full dataset is available as `df` with columns already normalized to lowercase snake_case.
- If WANT_CHART is False:
    * Do NOT create charts.
    * Compute the result and assign a pandas DataFrame to `answer_df` when tabular,
      and/or a short string summary to `answer_text`.
- If WANT_CHART is True:
    * Create exactly one matplotlib chart and assign the Figure to `fig`.
    * Optionally also set `answer_text` or `answer_df` if useful.
- Do NOT save files or call plt.show(); caller handles saving/rendering.
- Output ONLY raw Python code, no backticks or explanations. No printing.
- Allowed imports: import pandas as pd; import matplotlib.pyplot as plt
"""

def ask_model_for_code(question: str, df_sample: list, model: str, temperature: float, max_tokens: int, want_chart: bool) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    payload = {"question": question, "want_chart": want_chart, "sample_records": df_sample[:100]}
    resp = client.responses.create(
        model=model or os.getenv("MODEL", "gpt-4o-mini"),
        temperature=temperature,
        max_output_tokens=max_tokens,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload)},
        ],
    )
    if getattr(resp, "output_text", None):
        return resp.output_text.strip()
    chunks = []
    for out in (getattr(resp, "output", None) or []):
        if getattr(out, "type", None) == "message":
            for c in (getattr(out, "content", None) or []):
                if getattr(c, "type", None) == "output_text" and getattr(c, "text", None):
                    chunks.append(c.text)
    return "\n".join(chunks).strip()
