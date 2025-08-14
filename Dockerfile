# syntax=docker/dockerfile:1
# check=error=true;experimental=all

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN useradd --create-home botuser && mkdir /Uploads && chown botuser:botuser /Uploads
USER botuser

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=botuser:botuser discord_embed /app/discord_embed

VOLUME ["/Uploads"]
EXPOSE 5000

CMD ["fastapi", "run", "discord_embed/main.py", "--proxy-headers", "--port", "5000", "--log-level", "debug", "--forwarded-allow-ips", "*"]
