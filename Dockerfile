# syntax=docker/dockerfile:1
# check=error=true;experimental=all

FROM --platform=$BUILDPLATFORM ghcr.io/jrottenberg/ffmpeg:7.1-scratch AS ffmpeg
FROM --platform=$BUILDPLATFORM python:3.13-slim-bookworm AS base
COPY --from=ffmpeg /bin/ffmpeg /bin/ffprobe /usr/local/bin/
COPY --from=ffmpeg /lib /lib
COPY --from=ffmpeg /share /share
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_CACHE=1

RUN useradd --create-home botuser && mkdir /Uploads && chown botuser:botuser /Uploads
USER botuser

WORKDIR /app
ADD --chown=botuser:botuser discord_embed /app/discord_embed

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev

VOLUME ["/Uploads"]
EXPOSE 5000

CMD ["uv", "run", "uvicorn", "discord_embed.main:app", "--host", "0.0.0.0", "--port", "5000", "--use-colors", "--proxy-headers", "--forwarded-allow-ips", "*", "--log-level", "debug"]
