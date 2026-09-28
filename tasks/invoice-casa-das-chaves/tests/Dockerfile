FROM python:3.13.7-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /uvx /usr/local/bin/
RUN uv pip install --system harbor-rewardkit==0.2.1
COPY . /tests/
WORKDIR /app
