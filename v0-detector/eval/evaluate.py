#!/usr/bin/env python3
"""v0 eval: accuracy of the judge against the labeled eval set.

    python eval/evaluate.py [--predictions eval/cached_predictions.jsonl] [--labels eval/v0_eval_labels.jsonl]

Matches predictions to labels on (session_id, turn_index, span) and reports accuracy, a confusion matrix, and
per-class precision/recall. The eval set covers every public session (1.9k claims).
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CLASSES = ["true", "false", "unverifiable", "premature"]


def load(path: str) -> dict[tuple, dict]:
    out = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            out[(r["session_id"], r["turn_index"], tuple(r["span"]))] = r
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", default=os.path.join(HERE, "cached_predictions.jsonl"))
    ap.add_argument("--labels", default=os.path.join(HERE, "v0_eval_labels.jsonl"))
    args = ap.parse_args()
    preds, labels = load(args.predictions), load(args.labels)
    keys = sorted(set(preds) & set(labels))
    correct = sum(1 for k in keys if preds[k]["verdict"] == labels[k]["verdict"])
    conf = defaultdict(Counter)
    for k in keys:
        conf[labels[k]["verdict"]][preds[k]["verdict"]] += 1
    acc = correct / len(keys)
    print(f"v0 judge eval")
    print(f"  claims evaluated : {len(keys)}  (predictions {len(preds)}, labels {len(labels)})")
    print(f"  accuracy         : {acc:.1%}")
    attr_keys = [k for k in keys if labels[k]["verdict"] == "false" and preds[k]["verdict"] == "false"]
    if attr_keys:
        attr_acc = sum(1 for k in attr_keys if preds[k].get("attribution") == labels[k].get("attribution")) / len(attr_keys)
        print(f"  attribution acc  : {attr_acc:.1%}  (on {len(attr_keys)} claims both sides flagged)")
    print()
    present = [c for c in CLASSES if any(conf[c].values()) or any(conf[r][c] for r in conf)]
    print("  confusion (rows = label, cols = prediction)")
    print("  " + " " * 14 + "".join(f"{c:>14}" for c in present))
    for r in present:
        print(f"  {r:>14}" + "".join(f"{conf[r][c]:>14}" for c in present))
    print()
    for c in present:
        tp = conf[c][c]
        fp = sum(conf[r][c] for r in present if r != c)
        fn = sum(conf[c][p] for p in present if p != c)
        p_ = tp / (tp + fp) if tp + fp else 0.0
        r_ = tp / (tp + fn) if tp + fn else 0.0
        print(f"  {c:>14}: precision {p_:.2f}  recall {r_:.2f}  support {tp + fn}")
    print()
    verdict = "ship" if acc >= 0.9 else "needs work"
    print(f"  conclusion: {acc:.1%} agreement with labels -> {verdict}")


if __name__ == "__main__":
    main()
