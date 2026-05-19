FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && python -m pip install .

RUN mkdir -p /app/.work /app/.state /app/.runtime /app/.exports

EXPOSE 8765

CMD ["python", "-m", "cloudpan_bridge.cli", "serve", "--config", "/app/.work/openlist-config.json", "--host", "0.0.0.0", "--port", "8765"]
