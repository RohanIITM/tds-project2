import re
from typing import List, Dict, Any, Tuple

ARRAY_HINT = re.compile(r"respond with a json array", re.I)
OBJECT_HINT = re.compile(r"respond with a json object", re.I)
CODE_FENCE = re.compile(r"```(json)?(.*?)```", re.S|re.I)

QUESTION_LINE = re.compile(r"^\s*(\d+)[\).] \s*(.+)$", re.I)


def extract_json_template(text: str) -> Tuple[str, Any]:
    """Returns template_type, template.
    template_type in {"array","object","none"}
    If object, returns parsed keys list; if array, returns count or 0.
    """
    if OBJECT_HINT.search(text):
        # Look for a fenced JSON object with keys
        for fence, body in CODE_FENCE.findall(text):
            body = body.strip()
            if body.startswith("{"):
                try:
                    import json
                    keys = list(json.loads(body).keys())
                    return "object", keys
                except Exception:
                    pass
        return "object", []
    if ARRAY_HINT.search(text):
        # Count numbered questions
        qs = [m.group(2).strip() for m in map(QUESTION_LINE.match, text.splitlines()) if m]
        return "array", len(qs) if qs else 0
    return "none", None


def split_numbered_questions(text: str) -> List[str]:
    qs: List[str] = []
    for line in text.splitlines():
        m = QUESTION_LINE.match(line)
        if m:
            qs.append(m.group(2).strip())
    return qs if qs else [text.strip()]
