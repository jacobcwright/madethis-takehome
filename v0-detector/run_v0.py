#!/usr/bin/env python3
"""v0 detector: LLM judge over agent turns.

    python run_v0.py <input_dir> <output_dir> [--model MODEL] [--cached-only]

For each session file in <input_dir>, writes <output_dir>/<session_id>.json in the submission format described in
INTERFACE.md. With ANTHROPIC_API_KEY set (and optionally ANTHROPIC_BASE_URL), every agent turn is judged live with
judge_prompt.md. Without a key, or with --cached-only, predictions are loaded from eval/cached_predictions.jsonl,
which holds the judge's output for every public session, so the eval suite runs end to end without spending anything.

Cost note: about 1.1k input tokens per agent turn, ~5 turns per session. At Sonnet prices that is well under a cent
per session, inside the CONSTRAINTS.md budget.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPT = open(os.path.join(HERE, "judge_prompt.md")).read()
CACHE = os.path.join(HERE, "eval", "cached_predictions.jsonl")
DEFAULT_MODEL = "claude-sonnet-4-5"


def exchange_for_turn(turns: list[dict], idx: int) -> str:
    """The owner request and tool calls since the previous agent turn, rendered for the judge."""
    start = 0
    for t in reversed(turns[:idx]):
        if t["role"] == "agent":
            start = t["turn_index"] + 1
            break
    lines = []
    for t in turns[start:idx]:
        if t["role"] == "owner":
            lines.append(f"OWNER: {t['content']}")
        elif t["role"] == "tool":
            lines.append(f"TOOL {t['tool_name']}({json.dumps(t.get('args', {}))}) -> {json.dumps(t.get('result', {}))}")
    lines.append(f"ASSISTANT: {turns[idx]['content']}")
    return "\n".join(lines)


def call_judge(model: str, exchange: str, retries: int = 3) -> list[dict]:
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    body = json.dumps({
        "model": model, "max_tokens": 1024, "temperature": 0,
        "system": PROMPT,
        "messages": [{"role": "user", "content": exchange}],
    }).encode()
    req = urllib.request.Request(f"{base}/v1/messages", data=body, method="POST", headers={
        "content-type": "application/json", "x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            text = "".join(b.get("text", "") for b in data.get("content", []))
            text = text[text.find("{"): text.rfind("}") + 1]
            return json.loads(text).get("claims", [])
        except (urllib.error.URLError, json.JSONDecodeError, KeyError, ValueError) as e:
            if attempt == retries - 1:
                print(f"judge failed: {e}", file=sys.stderr)
                return []
            time.sleep(1.5 * (attempt + 1))
    return []


def locate(content: str, text: str) -> list[int] | None:
    i = content.find(text)
    if i < 0:
        i = content.lower().find(text.lower())
    return [i, i + len(text)] if i >= 0 else None


def judge_live(doc: dict, model: str) -> dict:
    claims = []
    for t in doc["turns"]:
        if t["role"] != "agent":
            continue
        for c in call_judge(model, exchange_for_turn(doc["turns"], t["turn_index"])):
            text = str(c.get("text", ""))
            if not text:
                continue
            claims.append({
                "turn_index": t["turn_index"], "span": locate(t["content"], text), "text": text,
                "category": c.get("category", "other"), "verdict": c.get("verdict", "true"),
                "attribution": c.get("attribution") if c.get("verdict") == "false" else None,
                "evidence": [x["call_id"] for x in doc["turns"] if x["role"] == "tool" and x["turn_index"] < t["turn_index"]][-3:],
                "confidence": float(c.get("confidence", 0.9)),
            })
    return {"session_id": doc["session_id"], "claims": claims}


def load_cache() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    with open(CACHE) as f:
        for line in f:
            row = json.loads(line)
            out.setdefault(row["session_id"], []).append({k: v for k, v in row.items() if k != "session_id"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir")
    ap.add_argument("output_dir")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--cached-only", action="store_true", help="never call the API; use eval/cached_predictions.jsonl")
    args = ap.parse_args()
    live = bool(os.environ.get("ANTHROPIC_API_KEY")) and not args.cached_only
    cache = None if live else load_cache()
    os.makedirs(args.output_dir, exist_ok=True)
    n = missing = 0
    for name in sorted(os.listdir(args.input_dir)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(args.input_dir, name)) as f:
            doc = json.load(f)
        if live:
            result = judge_live(doc, args.model)
        else:
            claims = cache.get(doc["session_id"])
            if claims is None:
                missing += 1
                claims = []
            result = {"session_id": doc["session_id"], "claims": claims}
        with open(os.path.join(args.output_dir, doc["session_id"] + ".json"), "w") as f:
            json.dump(result, f, indent=1)
        n += 1
    mode = f"live ({args.model})" if live else "cached"
    print(f"v0: wrote {n} sessions ({mode}){'; ' + str(missing) + ' sessions had no cached predictions' if missing else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
