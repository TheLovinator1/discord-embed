FROM python:3.10-slim

# We don't want apt-get to interact with us and we want the default answers to be used for all questions.
ARG DEBIAN_FRONTEND=noninteractive

# Don't generate byte code (.pyc-files).
# These are only needed if we run the python-files several times.
# Docker doesn't keep the data between runs so this adds nothing.
ENV PYTHONDONTWRITEBYTECODE 1

# Force the stdout and stderr streams to be unbuffered.
# Will allow log messages to be immediately dumped instead of being buffered.
# This is useful when the bot crashes before writing messages stuck in the buffer.
ENV PYTHONUNBUFFERED 1

# Update packages and install needed packages to build our requirements.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc curl git ffmpeg python-is-python3

# Create user so we don't run as root.
RUN useradd --create-home botuser

# Make log directory
RUN \
mkdir -p /var/log/discord-embed/ && chown -R botuser:botuser /var/log/discord-embed/ && \
mkdir /Uploads && chown -R botuser:botuser /Uploads

VOLUME ["/Uploads"]

# Change to the user we created.
USER botuser

# Install poetry.
RUN curl -sSL https://install.python-poetry.org | python -

# Add poetry to our path.
ENV PATH="/home/botuser/.local/bin/:${PATH}"

# Copy files from our repository to the container.
ADD --chown=botuser:botuser pyproject.toml poetry.lock README.md LICENSE /home/botuser/discord-embed/

# Change directory to where we will run the bot.
WORKDIR /home/botuser/discord-embed

# Install the requirements.
RUN poetry install --no-interaction --no-ansi --no-dev && \
poetry add uvicorn[standard]

# Add main.py and settings.py to the container.
ADD --chown=botuser:botuser discord_embed /home/botuser/discord-embed/discord_embed/

EXPOSE 5000

CMD ["poetry", "run", "uvicorn", "discord_embed.main:app", "--host", "0.0.0.0", "--port", "5000"]
