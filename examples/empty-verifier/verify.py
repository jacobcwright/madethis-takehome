#!/usr/bin/env python3
"""The smallest valid verifier: reads every session, writes an output with zero claims.

    verify /input /output

Replace the body of `verify_session` with your system. Keep the file-per-session contract.
"""

import json
import os
import sys


def verify_session(doc: dict) -> dict:
    return {"session_id": doc["session_id"], "claims": []}


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: verify <input_dir> <output_dir>", file=sys.stderr)
        return 2
    in_dir, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    for name in sorted(os.listdir(in_dir)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(in_dir, name)) as f:
            doc = json.load(f)
        result = verify_session(doc)
        with open(os.path.join(out_dir, result["session_id"] + ".json"), "w") as f:
            json.dump(result, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
