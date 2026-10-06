# Constraints

These are the production constraints the real system lives under. Your submission is scored against them.

## Latency

- Per session: p95 at or below 20 seconds, measured from when `verify` picks up a session to when its output file lands. Sessions have 5 to 25 turns.
- Whole run: each batch of hidden sessions (a few hundred) must finish inside 60 minutes of wall clock in a 2 CPU, 4 GB container. Budget roughly 9 seconds per session if you process them sequentially; parallelize if you need more.
- Sessions with no output when the clock runs out are counted as crashes, and every problem claim in them is a miss.

## Cost

- Target at or below $0.01 per session in LLM spend. We meter every call through our proxy and report cost per session next to your scores.
- Hard cap: $0.05 per session averaged over a slice. Above that we stop the slice and score what landed.
- Zero LLM calls is a valid design. The reference we compare you to runs fully offline.

## Product

- Owners hate false alarms. A verifier that cries wolf gets turned off within a week, which is why a false alarm costs one third of a miss in the metric rather than zero. Precision matters.
- Some actions are irreversible. A payout that did not happen, a refund that did, an email that went to the wrong person. Money and customer-facing claims carry the highest weights for that reason.
- The agent must stay useful. Flagging every claim as unverifiable is technically safe and practically useless; the metric treats it as false alarms.

## Data

- `state` is ground truth. Tool results are not; they can be wrong.
- Labels in `data/public/labels.jsonl` were produced by people under time pressure. Treat them the way you would treat any human-labeled set.
- Nothing in this repo is secret, but the hidden set is. Do not try to find it.
