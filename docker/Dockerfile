FROM ghcr.io/astral-sh/uv:python3.12-alpine

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen
COPY . .

CMD ["uv", "run", "main.py"]