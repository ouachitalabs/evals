FROM python:3.13.7-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /uvx /usr/local/bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends tmux=3.3a-3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
