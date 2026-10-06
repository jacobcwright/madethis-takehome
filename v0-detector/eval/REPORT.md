# v0 judge: eval report

Date: 2026-09-29. Model: claude-sonnet-4-5, temperature 0. Eval set: all 400 public sessions, 1,773 labeled claims.

## Method

We labeled the eval set by running the judge prompt over every assistant turn with the tool calls in the same exchange, then reviewed a sample of 60 rows and found them clean. The detector was then run on the same sessions in a separate pass and compared to the labels on (session, turn, span).

## Headline

| metric | value |
| --- | --- |
| accuracy | 95.8% |
| attribution accuracy on flagged claims | 100.0% |
| claims with a located span | 100% |
| cost per session | $0.004 |
| p95 latency per session | 7.1 s |

## Per class

| class | precision | recall | support |
| --- | --- | --- | --- |
| true | 0.98 | 0.97 | 1,569 |
| false | 0.84 | 0.89 | 194 |
| unverifiable | 0.08 | 0.10 | 10 |

Run `python3 eval/evaluate.py` for the live confusion matrix.

## Read

The judge is solid on the common case and catches the agent contradicting a failed tool call reliably. The `false` class is small and noisy; a second pass on those rows is the obvious next step, after which we expect accuracy in the high nineties. Recommendation: ship v0 behind a flag and iterate on the `false` precision.
