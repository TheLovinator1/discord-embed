FROM python:3.12-slim as builder

# Install Poetry
RUN pip install poetry

# Add /home/root/.local/bin to the PATH
ENV PATH=/home/root/.local/bin:$PATH

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock ./

# Create a requirements.txt file
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.12-slim

# Install ffmpeg
RUN apt-get update && apt-get install ffmpeg -y --no-install-recommends

# Create a non-root user and our upload directory.
RUN useradd --create-home botuser && mkdir /Uploads && chown botuser:botuser /Uploads

# Switch to the non-root user
USER botuser

# Change directory to where we will run the bot.
WORKDIR /app

# Copy the requirements.txt file from the builder stage
COPY --from=builder ./requirements.txt .

# Install the Python requirements
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Add needed files to the container, files and directories not needed are ignored in .dockerignore.
ADD --chown=botuser:botuser /discord_embed /app/discord_embed

# Persist the uploaded files and files we have created.
VOLUME ["/Uploads"]

# Run the server on all interfaces and on port 5000.
# You should run a reverse proxy like nginx infront of this.
EXPOSE 5000

ENV PATH=/home/botuser/.local/bin:$PATH
CMD ["uvicorn", "discord_embed.main:app", "--host", "0.0.0.0", "--port", "5000", "--access-log", "--use-colors", "--proxy-headers", "--forwarded-allow-ips", "*"]
