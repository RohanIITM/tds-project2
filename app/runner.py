# app/process_queries.py
import json
import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

from app.tool.llm import complete  # your proxy OpenAI client
from app.tool.plot import scatter_with_regression
from app.tool.tables import Tables
from app.tool.web import Web

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def extract_relevant_table(html: str) -> tuple[pd.DataFrame, list[str]]:
    """
    Extract the most relevant table from HTML and determine numeric columns heuristically.
    """
    tables = pd.read_html(html, flavor="lxml")
    if not tables:
        raise RuntimeError("No tables found in HTML")

    best_table: pd.DataFrame | None = None
    numeric_cols: list[str] = []
    max_numeric = -1

    for t in tables:
        t2 = t.copy()
        # normalize column names
        t2.columns = [re.sub(r"\W+", "_", str(c)).strip("_").lower() for c in t2.columns]

        # find numeric columns
        nums: list[str] = []
        for c in t2.columns:
            sample = pd.to_numeric(t2[c].iloc[:10], errors="coerce")
            if sample.notna().sum() > 0:
                nums.append(c)

        if len(nums) > max_numeric:
            max_numeric = len(nums)
            best_table = t2
            numeric_cols = nums

    if best_table is None or not numeric_cols:
        raise RuntimeError("Could not identify a table with numeric columns")

    logger.info(f"Selected table with numeric columns: {numeric_cols}")
    return best_table, numeric_cols


def clean_llm_output(text: str) -> str:
    """
    Remove markdown code fences if present to safely parse JSON.
    """
    return re.sub(r"^```(?:json|plaintext)?|```$", "", text.strip(), flags=re.I | re.M)


async def process_questions(
    questions_path: Path, attachments_dir: Path | None = None
) -> list[dict[str, Any]]:
    """
    Reads questions.txt, fetches table if URL is present, sends all questions to LLM,
    parses answers, and returns a list of dicts.
    """
    questions = [q.strip() for q in questions_path.read_text(encoding="utf-8").splitlines() if q.strip()]
    answers: list[dict[str, Any]] = []

    # Load attachments into dataframes (if any)
    dataframes: list[pd.DataFrame] = []
    if attachments_dir and attachments_dir.exists():
        for file in attachments_dir.iterdir():
            if file.suffix.lower() == ".csv":
                dataframes.append(pd.read_csv(file))
            elif file.suffix.lower() in (".xls", ".xlsx"):
                dataframes.append(pd.read_excel(file))

    # Check if any question contains a URL
    table_df: pd.DataFrame | None = None
    numeric_cols: list[str] = []

    for q in questions:
        url_match = re.search(r"(https?://\S+)", q)
        if url_match:
            url = url_match.group(1)
            logger.info(f"Fetching table from URL: {url}")
            html = Web.get(url)
            table_df, numeric_cols = extract_relevant_table(html)
            break  # only fetch first table, LLM will use it for all questions

    # Prepare data for LLM
    table_json = table_df.head(20).to_dict(orient="records") if table_df is not None else []

    # Construct system prompt with example
    system_prompt = f"""
You are a helpful data analyst. Use the table provided to answer questions.
- Always return a JSON array of answers, in the same order as questions.
- Do NOT include markdown, code fences, or extra text.
- If a question asks for a plot, return a base64-encoded data URI under 100KB.

Example:

Questions:
Scrape the list of highest grossing films from Wikipedia. It is at the URL:
https://en.wikipedia.org/wiki/List_of_highest-grossing_films

Answer the following questions and respond with a JSON array of strings containing the answer.

1. How many $2 bn movies were released before 2000?
2. Which is the earliest film that grossed over $1.5 bn?
3. What's the correlation between the Rank and Peak?
4. Draw a scatterplot of Rank and Peak along with a dotted red regression line through it.
   Return as a base-64 encoded data URI, `"data:image/png;base64,iVBORw0KG..."` under 100,000 bytes.

Expected JSON answer:
[1, "Titanic", 0.485782, "data:image/png;base64,iVBORw0KG... (response truncated)"]

Now answer the following questions with the actual table:

Table columns: {numeric_cols}
Table data (first 20 rows): {json.dumps(table_json)}
Questions:
{json.dumps(questions, indent=2)}
"""

    logger.info("Sending questions and table to LLM for answers...")
    llm_output = complete(system=system_prompt, user="")
    logger.info(f"llm_output='{llm_output[:200]}...'")  # truncate for logging

    try:
        cleaned = clean_llm_output(llm_output)
        llm_answers = json.loads(cleaned)
    except Exception as e:
        logger.error(f"Failed to parse LLM output: {e}")
        llm_answers = [f"(Failed to answer question {i+1})" for i in range(len(questions))]

    return llm_answers
