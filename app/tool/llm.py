import json
import logging
import os

import requests

logger = logging.getLogger(__name__)

# Get proxy token from env (or wherever you store it)
OPENAI_PROXY_TOKEN = os.getenv("OPENAI_PROXY_TOKEN")
if not OPENAI_PROXY_TOKEN:
    logger.warning("OPENAI_PROXY_TOKEN not set; LLM calls will fail.")

OPENAI_PROXY_URL = "https://aipipe.org/openrouter/v1/chat/completions"


def complete(system: str, user: str) -> str:
    """
    Send a system + user prompt to OpenAI via AI Pipe / OpenRouter proxy.
    Returns the text completion.
    """
    if not OPENAI_PROXY_TOKEN:
        logger.error("No proxy token available.")
        return ""

    payload = {
        "model": "openai/gpt-4.1-nano",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_PROXY_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            OPENAI_PROXY_URL, headers=headers, data=json.dumps(payload), timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        # extract text from OpenRouter response
        choices = data.get("choices")
        if choices and isinstance(choices, list):
            return choices[0].get("message", {}).get("content", "")
        return ""
    except Exception as e:
        logger.error(f"OpenAI proxy request failed: {e}")
        return ""
