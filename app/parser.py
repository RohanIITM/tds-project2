
import re
from typing import List, Tuple, Dict
from app.utils.text import extract_json_template, split_numbered_questions

URL_RE = re.compile(r"https?://\S+", re.I)

class ParsedTask:
    def __init__(self, raw: str):
        self.raw = raw
        self.questions: List[str] = split_numbered_questions(raw)
        self.template_kind, self.template = extract_json_template(raw)
        self.urls = URL_RE.findall(raw)
