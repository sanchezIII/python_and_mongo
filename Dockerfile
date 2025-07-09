# Use Python 3.9 slim image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH="/app/src:$PYTHONPATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Configure Poetry to create venv in project directory
RUN poetry config virtualenvs.in-project true

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Change ownership of app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies as appuser
RUN poetry install --only main --no-root

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["poetry", "run", "python", "-m", "src.app"] 