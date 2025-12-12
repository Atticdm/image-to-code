FROM python:3.12.3-slim-bullseye

ENV POETRY_VERSION=2.1.3
# Suppress SyntaxWarnings from moviepy library (known issue in moviepy 1.0.3)
ENV PYTHONWARNINGS=ignore::SyntaxWarning

# Install system dependencies
RUN pip install "poetry==$POETRY_VERSION"

# Set work directory
WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /app/

# Disable the creation of virtual environments
RUN poetry config virtualenvs.create false

# Ensure lockfile is compatible/synced with pyproject.toml.
RUN poetry lock

# Install dependencies
RUN poetry install --only main --no-interaction --no-ansi

# Copy the current directory contents into the container at /app
COPY ./ /app/

# Expose port (Railway will set PORT env variable)
EXPOSE 7001

# Start command (Railway provides PORT env variable)
# Use shell to properly substitute PORT variable, default to 7001 if not set
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7001}"]
