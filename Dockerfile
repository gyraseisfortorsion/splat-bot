FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY bot ./bot
COPY data ./data

# Install dependencies with uv
RUN uv pip install --system -r pyproject.toml

# Run the bot
CMD ["python", "-m", "bot.main"]
