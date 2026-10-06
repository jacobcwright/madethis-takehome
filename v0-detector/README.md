# v0 detector

Our current approach. An LLM judge reads each assistant turn together with the tool calls from the same exchange and lists the claims it finds with a verdict. Prompt in `judge_prompt.md`, runner in `run_v0.py`.

## Results

96% accuracy against the labeled eval set (`eval/v0_eval_labels.jsonl`, 1.9k claims covering all 400 public sessions). Full numbers in `eval/REPORT.md`; reproduce them with:

```sh
python3 eval/evaluate.py
```

## Running it

```sh
# with a key: live judging (about $0.004 per session at Sonnet prices)
export ANTHROPIC_API_KEY=...
python3 run_v0.py ../data/public/sessions /tmp/v0-out

# without a key: replays eval/cached_predictions.jsonl, which holds the judge's output for every public session
python3 run_v0.py ../data/public/sessions /tmp/v0-out --cached-only
```

The output is in the submission format, so you can also run `../score_public.py /tmp/v0-out` on it, wrap `run_v0.py` in a Dockerfile, and submit it as is if you think it is good enough.

## Known gaps

- Latency: about 1.2 s per agent turn with Sonnet, sequential. Fine for the budget but there is headroom to parallelize.
- The judge occasionally quotes the claim text with small edits, which makes `span` null for that claim. Text matching covers it.
