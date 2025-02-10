FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get install ffmpeg -y --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home botuser && mkdir /Uploads && chown botuser:botuser /Uploads
USER botuser

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project

ADD --chown=botuser:botuser /discord_embed /app/discord_embed

VOLUME ["/Uploads"]

EXPOSE 5000

CMD ["uv", "run", "uvicorn", "discord_embed.main:app", "--host", "0.0.0.0", "--port", "5000", "--use-colors", "--proxy-headers", "--forwarded-allow-ips", "*", "--log-level", "debug"]
