import os
import json
import hashlib
import time
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_URL = "https://api.anthropic.com/v1/messages"
API_KEY = os.getenv("CLAUDE_API_KEY")
CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def ask(prompt: str,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 256,
        retries: int = 3,
        pause: float = 1.0) -> str:
    """Return Claude's reply to *prompt*. Uses on-disk caching and retry."""
    if not API_KEY:
        raise RuntimeError("CLAUDE_API_KEY environment variable is not set")
    
    key = hashlib.sha256(prompt.encode()).hexdigest()
    cache_path = CACHE_DIR / f"{key}.json"

    if cache_path.exists():
        with cache_path.open() as fp:
            cached = json.load(fp)
        return cached["content"][0]["text"]

    headers = {
        "x-api-key": API_KEY,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }

    last_error = None
    for _ in range(retries):
        try:
            resp = requests.post(API_URL, headers=headers,
                                 json=body, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                with cache_path.open("w") as fp:
                    json.dump(data, fp)
                return data["content"][0]["text"]
            last_error = f"{resp.status_code}: {resp.text}"
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_error = str(exc)
        time.sleep(pause)

    raise RuntimeError(
        f"Anthropic request failed after {retries} attempts. "
        f"Last error: {last_error}"
    )
