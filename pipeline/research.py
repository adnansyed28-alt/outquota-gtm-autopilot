import json
import os
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOMEPAGES = os.path.join(ROOT, "sample-data", "homepages")
PROMPT_PATH = os.path.join(ROOT, "prompts", "company_research.txt")
OUT_PATH = os.path.join(ROOT, "sample-data", "research_output.json")
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
RETRY_CODES = {429, 500, 503}  # temporary errors worth retrying
DELAY_BETWEEN_CALLS = 12       # seconds, to stay under free-tier rate limits


def load_key():
    """Read the API key from .env (never hard-code it)."""
    with open(os.path.join(ROOT, ".env")) as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                return line.strip().split("=", 1)[1]
    raise SystemExit("GEMINI_API_KEY not found in .env")


def call_api(body, key, attempts=4):
    """POST to the API, retrying temporary errors with a growing wait."""
    for attempt in range(1, attempts + 1):
        try:
            resp = requests.post(URL, headers={"x-goog-api-key": key}, json=body, timeout=90)
        except requests.RequestException as err:
            if attempt < attempts:
                wait = 2 ** attempt
                print(f"  Network problem ({type(err).__name__}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise RuntimeError(f"Network error: {err}")
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code in RETRY_CODES and attempt < attempts:
            wait = 30 * attempt if resp.status_code == 429 else 2 ** attempt
            print(f"  API busy ({resp.status_code}), retrying in {wait}s (attempt {attempt}/{attempts})...")
            time.sleep(wait)
            continue
        raise RuntimeError(f"API error {resp.status_code}: {resp.text[:200]}")


def research(text, prompt, key):
    body = {
        "contents": [{"parts": [{"text": f"{prompt}\n\nHOMEPAGE TEXT:\n{text}"}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    data = call_api(body, key)
    parts = data["candidates"][0]["content"]["parts"]
    answer = next(p["text"] for p in parts if "text" in p)
    return json.loads(answer)


def save(results):
    with open(OUT_PATH, "w") as f:
        json.dump(results, f, indent=2)


def main():
    key = load_key()
    prompt = open(PROMPT_PATH).read()

    results = {}
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            old = json.load(f)
        results = {k: v for k, v in old.items() if "error" not in v}  # keep only successes
    print(f"Already researched: {len(results)} companies (these are skipped)")

    made_a_call = False
    for name in sorted(os.listdir(HOMEPAGES)):
        company = name.replace(".txt", "")
        if company in results:
            continue
        if made_a_call:
            time.sleep(DELAY_BETWEEN_CALLS)
        made_a_call = True
        text = open(os.path.join(HOMEPAGES, name)).read()
        print(f"\n=== {company} ===")
        try:
            results[company] = research(text, prompt, key)
        except RuntimeError as err:
            print(f"  FAILED: {err}")
            save(results)
            if "429" in str(err):
                print("\nQuota exhausted. Progress is saved. Wait a few minutes (or until tomorrow) and run again; "
                      "finished companies will be skipped.")
                break
            continue
        print(json.dumps(results[company], indent=2))
        save(results)

    total = len(os.listdir(HOMEPAGES))
    print(f"\nDone: {len(results)} of {total} companies researched. Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
