# syntax=docker/dockerfile:1
# check=error=true;experimental=all

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN useradd --create-home botuser && mkdir /Uploads && chown botuser:botuser /Uploads
USER botuser
ENV PATH="${PATH}:/home/botuser/.local/bin"

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=botuser:botuser discord_embed /app/discord_embed

VOLUME ["/Uploads"]
EXPOSE 5000

CMD ["python", "-m", "uvicorn", "discord_embed.main:app", "--host", "0.0.0.0", "--port", "5000", "--use-colors", "--proxy-headers", "--forwarded-allow-ips", "*", "--log-level", "debug"]