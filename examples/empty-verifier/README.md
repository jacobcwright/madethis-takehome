# empty-verifier

The smallest image that passes the interface check. It outputs no claims, so it scores zero. Use it to confirm your Docker setup and the output format before building anything.

```sh
cd examples/empty-verifier
docker build -t empty-verifier .
mkdir -p /tmp/out
docker run --rm -v "$PWD/../../data/public/sessions:/input:ro" -v /tmp/out:/output empty-verifier verify /input /output
python3 ../../score_public.py /tmp/out --labels ../../data/public/labels.jsonl --sessions ../../data/public/sessions
```

`sample_output/` holds one output file in the exact shape the scorer expects, with a couple of example claims.
