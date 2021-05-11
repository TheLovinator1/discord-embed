# We need gcc, build-essential and git to install our requirements but we 
# don't need them when run the application so we can selectively copy artifacts
# from this stage (compile-image) to second one (runtime-image), leaving 
# behind everything we don't need in the final build. 
FROM python:3.9-slim AS compile-image

# We don't want apt-get to interact with us,
# and we want the default answers to be used for all questions.
# Is it also completely silent and unobtrusive.
ARG DEBIAN_FRONTEND=noninteractive

# Update packages and install needed packages to build our requirements.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc git

# Create new virtual environment in /opt/venv and change to it.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy and install requirements.
COPY requirements.txt .
RUN pip install --disable-pip-version-check --no-cache-dir --requirement requirements.txt

# Change to our second stage. This is the one that will run the application.
FROM python:3.9-slim AS runtime-image
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg
# Copy Python dependencies from our build image.
COPY --from=compile-image /opt/venv /opt/venv



# Create user so we don't run as root.
RUN useradd --create-home botuser

# Create directories we need
RUN mkdir -p /home/botuser/Uploads/a && mkdir -p /home/botuser/templates

# Change ownership of directories
RUN chown -R botuser:botuser /home/botuser && chmod -R 755 /home/botuser

# Change user
USER botuser

# Change directory to where we will run the application.
WORKDIR /home/botuser

# Copy our Python application to our home directory.
COPY main.py ./
COPY Uploads/ ./Uploads
COPY templates/ ./templates

# Don't generate byte code (.pyc-files). 
# These are only needed if we run the python-files several times.
# Docker doesn't keep the data between runs so this adds nothing.
ENV PYTHONDONTWRITEBYTECODE 1

# Force the stdout and stderr streams to be unbuffered. 
# Will allow log messages to be immediately dumped instead of being buffered. 
# This is useful when the application crashes before writing messages stuck in the buffer.
# Has a minor performance loss. We don't have many log messages so probably makes zero difference.
ENV PYTHONUNBUFFERED 1

# Use our virtual environment that we created in the other stage.
ENV PATH="/opt/venv/bin:$PATH"

# Make the website accessible outside localhost
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the web port
EXPOSE 5000

# Run bot.
CMD [ "gunicorn", "--workers=2", "--threads=4", "--log-file=-", "--bind=0.0.0.0:5000", "main:app"]
