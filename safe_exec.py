import os, re
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    def norm(c: str) -> str:
        c = c.strip().lower()
        c = re.sub(r"[^0-9a-z]+", "_", c)
        c = re.sub(r"_+", "_", c).strip("_")
        return c
    out = df.copy()
    out.columns = [norm(c) for c in out.columns]
    return out

def _unwrap(text: str) -> str:
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

def _normalize_df_name(code: str) -> str:
    code = re.sub(r"\bdffd\b", "df", code)
    code = re.sub(r"\bdfd\b", "df", code)
    code = re.sub(r"\bdff\b", "df", code)
    code = re.sub(r"\bdataframe\b", "df", code, flags=re.IGNORECASE)
    return code

def _save_chart(fig) -> str:
    os.makedirs("charts", exist_ok=True)
    name = f"plot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    path = os.path.join("charts", name)
    fig.savefig(path, bbox_inches="tight")
    return path

def run_generated_code(code: str, df: pd.DataFrame, want_chart: bool, save_files: bool = False):
    clean = _unwrap(code)
    clean = _normalize_df_name(clean)

    for banned in ["subprocess", "os.system(", "open(", "eval(", "exec(", "requests", "urllib"]:
        if banned in clean:
            return {"error": f"Blocked unsafe usage: {banned}"}

    local_vars = {
        "df": df,
        "pd": pd,
        "plt": plt,
        "answer_text": None,
        "answer_df": None,
        "fig": None,
        "WANT_CHART": want_chart,
    }

    if not want_chart and ("plt." in clean or "savefig" in clean):
        return {"error": "Chart not allowed in text-only mode."}

    try:
        exec(clean, {}, local_vars)
    except Exception as e:
        return {"error": f"Code execution error: {e}"}

    out = {}

    # Preferred contract: answer_df
    if isinstance(local_vars.get("answer_df"), pd.DataFrame):
        out["dataframe"] = local_vars["answer_df"]
    else:
        # Fallback: pick any DataFrame created (common when model forgets the name)
        dfs = [v for v in local_vars.values() if isinstance(v, pd.DataFrame)]
        if dfs:
            out["dataframe"] = dfs[-1]  # take the last created

    if isinstance(local_vars.get("answer_text"), str) and local_vars["answer_text"].strip():
        out["text"] = local_vars["answer_text"]

    if want_chart and local_vars.get("fig") is not None:
        out["figure"] = local_vars["fig"]
        if save_files:
            try:
                out["saved_path"] = _save_chart(local_vars["fig"])
            except Exception as e:
                out["error"] = f"Error saving chart: {e}"

    return out
