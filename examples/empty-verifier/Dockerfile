# Minimal image that satisfies the interface: an executable `verify` on PATH.
FROM python:3.12-slim
WORKDIR /app
COPY verify.py /usr/local/bin/verify
RUN chmod +x /usr/local/bin/verify
# No ENTRYPOINT on purpose: the grader runs `docker run <image> verify /input /output`.
CMD ["verify", "/input", "/output"]
