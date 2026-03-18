FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN chmod +x /app/docker/entrypoint.sh
RUN uv sync --frozen --no-dev

EXPOSE 8000

ENTRYPOINT ["sh", "/app/docker/entrypoint.sh"]
