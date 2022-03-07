# We need gcc, build-essential and git to install our requirements but we 
# don't need them when run the application so we can selectively copy artifacts
# from this stage (compile-image) to second one (runtime-image), leaving 
# behind everything we don't need in the final build. 
FROM python:3.10-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.10-slim

# TODO: Remove this
# We don't want apt-get to interact with us,
# and we want the default answers to be used for all questions.
ARG DEBIAN_FRONTEND=noninteractive

# Update packages and install needed packages to build our requirements.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential ffmpeg

# Create user so we don't run as root.
RUN useradd --create-home botuser

# Change ownership of directories
RUN chown -R botuser:botuser /home/botuser && chmod -R 755 /home/botuser

# Change user
USER botuser

# Change directory to where we will run the application.
WORKDIR /home/botuser

ENV PATH "$PATH:/home/botuser/.local/bin"

# Copy our Python application to our home directory.
COPY --from=requirements-stage /tmp/requirements.txt /home/botuser/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /home/botuser/requirements.txt

COPY main.py ./

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

# Expose the web port
EXPOSE 5000

# Run bot.
CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "5000"]
