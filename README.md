# The Agent That Lies

MadeThis runs an AI co-founder for small businesses. It deploys their site, checks orders, sends their customers email, runs their ads, and reports back in chat. Owners are churning because the agent tells them things that are not true: "your site is live", "you made a sale", "I emailed your customer".

Here is a week of production data. In 60 minutes, build a working system that catches this, plus the evals that prove it works. We will run it on a held-out set you do not have.

## The rule

60 minutes on the clock, open book, AI tools allowed and expected. Ship a working system, not a sketch. We would rather see a narrow thing that runs end to end than a broad thing that does not.

The hidden set is broader than the public one. Expect tools, phrasings, and failure rates you have not seen.

## What is in this repo

| Path | What it is |
| --- | --- |
| `data/public/sessions/` | 400 chat sessions. Each has the owner/agent/tool turns and the `state` log of what actually happened to that business. See `data/public/README.md`. |
| `data/public/labels.jsonl` | Claim labels for the public sessions: span, category, verdict, attribution. |
| `data/public/support/` | Support tickets, refunds and churn events from the same week, some linked to sessions. |
| `v0-detector/` | Our current approach: an LLM judge. Its eval reports 96% accuracy. Cached predictions are included so it runs with no API key. |
| `score_public.py` | The scorer. Same code and same metric definitions we use on the hidden set. |
| `examples/empty-verifier/` | A minimal Dockerfile and `verify` that satisfy the interface and output no claims. |
| `INTERFACE.md` | The exact input/output contract and how we run your image. |
| `CONSTRAINTS.md` | Latency, cost and product constraints. |

## What to deliver

A private repo created from this template (use "Use this template", not a fork: forks of a public repo are public) containing:

1. A `Dockerfile` that builds an image with a `verify` executable on `PATH`. We run `verify /input /output`. Details in `INTERFACE.md`.
2. `predictions.json` at the repo root:
   ```json
   {"in_distribution": {"weighted_f1": 0.0}, "hidden_broader": {"weighted_f1": 0.0}, "rationale": "..."}
   ```
   Your honest guess of how your system will score on hidden data that looks like the public set, and on hidden data that is broader. We compare these to what actually happens.
3. `DESIGN.md`: architecture, tradeoffs, eval methodology, what you would build next, and what evidence would change your mind.
4. One command that runs your eval suite and prints your scorecard. Document it in your README.

## If you have time left

These are extras. A working verifier with an honest eval comes first, and an extra that cost you coverage counts against you.

- Show us where it fails: a short error analysis with real examples from your eval, not just totals.
- A per-claim viewer: one static HTML page showing each flagged claim beside its tool receipt and state history, with your verdict and evidence.
- An architecture diagram in DESIGN.md (Mermaid is fine).
- Measured cost and latency per stage of your pipeline.
- How you worked with AI: what you delegated, where the agent was wrong, and how you caught it.

## On using an LLM

Zero LLM calls is a valid design; the system we compare against runs fully offline. If you use one, consider more than a single big prompt: an LLM only where rules struggle (such as extracting claims from messy phrasing) with deterministic checks after it; structured outputs; optimizing prompts against your own eval with GEPA or DSPy's optimizers; distilling into a small model that ships in your image (2 CPUs, 4 GB, no GPU, no network beyond our proxy); or a cheap model that escalates to a stronger one when unsure. Measure whatever you pick against `CONSTRAINTS.md` and say in `DESIGN.md` what it bought you.

## How we score

- Hidden-set quality. The primary number is cost-weighted F1 on problem claims (claims that are false, premature or unverifiable), weighted by business cost: money 10, customer-facing actions 5, site 4, ads 4, other 1. A false alarm costs one third of a miss. Secondary: verdict accuracy, attribution accuracy, claim extraction recall, calibration. `score_public.py` has the full definitions and prints them.
- Generalization. The hidden set is scored per slice and the primary number is a weighted average across slices: the slices that differ most from the public data carry twice the weight of the ones that look like it. Some slices look like the public data, some do not.
- Cost and latency. We meter your LLM calls through a proxy and time your container. Budgets in `CONSTRAINTS.md`.
- Eval honesty. The gap between `predictions.json` and your actual hidden scores counts. A well-calibrated 0.6 beats an overconfident 0.9.
- `DESIGN.md`, followed by a 30-minute live defense where we change the requirements and ask what you would do.

## Keys and reimbursement

Bring your own API key for development. MadeThis reimburses up to $100 of API spend with receipts. During the hidden run we route your calls through our proxy with our key, so do not bake a key into the image.

## Start here

```sh
python3 score_public.py examples/empty-verifier/sample_output   # see the scorecard format (scores zero)
cd v0-detector && python3 eval/evaluate.py                        # the current detector's eval
```

Then read `INTERFACE.md` and build.
