import os
import shutil
import tempfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile

from .runner import process_questions

app = FastAPI(
    title="Data Analyst Agent API",
    description="API to process analytical questions, datasets, and generate outputs using LLM.",
    version="1.0.0",
)


@app.post("/api/")
async def analyze_api(
    questions: UploadFile = File(...), attachments: list[UploadFile] = File(default=[])
):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Save questions
        questions_path = tmp_path / "questions.txt"
        with open(questions_path, "wb") as f:
            shutil.copyfileobj(questions.file, f)

        # Save attachments
        attachments_dir = tmp_path / "attachments"
        attachments_dir.mkdir(exist_ok=True)
        for att in attachments:
            with open(attachments_dir / att.filename, "wb") as f:
                shutil.copyfileobj(att.file, f)

        # Process questions using LLM + tools
        answers = await process_questions(questions_path, attachments_dir)
        return answers


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Data Analyst Agent API running with LLM support",
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
