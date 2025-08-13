from typing import Dict, List, Tuple
from fastapi import UploadFile

async def read_uploads(files: List[UploadFile]) -> Dict[str, bytes]:
    blobs = {}
    for f in files:
        blobs[f.filename] = await f.read()
    return blobs

def find_questions(blobs: Dict[str, bytes]) -> str:
    for name in blobs:
        if name.lower().endswith("questions.txt") or name.lower() == "questions.txt":
            return blobs[name].decode("utf-8", errors="replace")
    raise ValueError("questions.txt is required but missing")
