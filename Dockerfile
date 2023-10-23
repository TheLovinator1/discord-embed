FROM python:3.12-slim
# TODO: Do the Poetry stuff in its own stage
# TODO: Add support for logging
# TODO: Add health check
# TODO: Add support for changing uid/gid
# TODO: Add support for changing host and port

# We don't want apt-get to interact with us and we want the default answers to be used for all questions.
ARG DEBIAN_FRONTEND=noninteractive

# Force the stdout and stderr streams to be unbuffered.
# Will allow log messages to be immediately dumped instead of being buffered.
# This is useful when the bot crashes before writing messages stuck in the buffer.
ENV PYTHONUNBUFFERED 1

# Update the system and install curl, it is needed for downloading Poetry.
RUN apt-get update && apt-get install curl ffmpeg -y --no-install-recommends

# 1. Create user so we don't run as root 
# 2. Create directories that the bot needs that are owned by the user.
#    /Uploads is used to store the uploaded files.
#    /home/botuser/discord-embed is where the Python code is stored.
RUN useradd --create-home botuser && \
    install --verbose --directory --mode=0775 --owner=botuser --group=botuser /Uploads /home/botuser/discord-embed

# Change to the user we created.
USER botuser

# Change directory to where we will run the bot.
WORKDIR /home/botuser/discord-embed

# Add needed files to the container, files and directories not needed are ignored in .dockerignore.
ADD --chown=botuser:botuser . /home/botuser/discord-embed/

# 1. Install Poetry.
# 2. Add Poetry to the PATH.
# 3. Install dependencies.
ENV PATH="/home/botuser/.local/bin/:$PATH"
RUN curl -sSL https://install.python-poetry.org | python -
RUN poetry install --no-interaction --no-ansi --only main

# Persist the uploaded files and files we have created.
VOLUME ["/Uploads"]

# Run the server on all interfaces and on port 5000.
# You should run a reverse proxy like nginx infront of this.
EXPOSE 5000
CMD ["poetry", "run", "uvicorn", "discord_embed.main:app", "--host", "0.0.0.0", "--port", "5000"]