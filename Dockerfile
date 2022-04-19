# We have two stages, one for making the virtual environment and
# installing the dependencies and another for running the uvicorn server.
# We use an virtual environment so we seperate the dependencies from the
# system-level dependencies.
FROM python:3.10-slim AS build-image

# Create virtual environment in /opt/venv, we will use this in the other
# stage.
RUN python -m venv /opt/venv

# Make sure we use the virtualenv.
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements.txt to the container, it was generated with
# 'poetry export -f requirements.txt --without-hashes'
# Note that if we pipe the output of the commmand to requirements.txt in
# Windows, it will be UTF-16 LE encoded.
COPY requirements.txt .

# Install the requirements.
RUN pip install -r requirements.txt

# This is the stage where we will run the uvicorn server.
FROM python:3.10-slim AS run-image

# Copy the virtual environment to the run-image.
COPY --from=build-image /opt/venv /opt/venv

# Install ffmpeg, it is needed for finding the video resolution and
# making the video thumbnail.
RUN apt-get update
RUN apt-get install -y --no-install-recommends ffmpeg

# Create user so we don't run as root and make the needed directories
# Logs are stored in /var/log/discord-embed and uploaded files,
# thumbnails, and HTML are stored in /Uploads.
RUN useradd --create-home botuser && \
install --verbose --directory --mode=0755 --owner=botuser --group=botuser /var/log/discord-embed/ /Uploads

# Persist the uploaded files and files we have created.
VOLUME ["/Uploads"]

# Change to the user we created so we don't run as root.
USER botuser

# Change directory to where we will run the bot.
WORKDIR /home/botuser/discord-embed

# Add main.py and settings.py to the container.
ADD --chown=botuser:botuser . /home/botuser/discord-embed/

# Uvicorn runs on port 5000, we can't use any ports below 1024 due to
# not being root.
EXPOSE 5000

# Make sure we use the virtualenv.
ENV PATH="/opt/venv/bin:$PATH"

# Don't generate byte code (.pyc-files).
# These are only needed if we run the python-files several times.
# Docker doesn't keep the data between runs so this adds nothing.
ENV PYTHONDONTWRITEBYTECODE 1

# Force the stdout and stderr streams to be unbuffered. This means that
# the output will be printed immediately instead of being buffered. If
# the Python application crashes, the output could be lost.
ENV PYTHONUNBUFFERED 1

# Run the server on all interfaces and on port 5000.
# You should run a reverse proxy like nginx infront of this.
CMD ["uvicorn", "discord_embed.main:app", "--host", "0.0.0.0", "--port", "5000"]
