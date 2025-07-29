# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt


# Stage 2: Final Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser

# Copy installed dependencies from builder stage
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Set ownership and permissions
RUN chown -R appuser:appuser /app
USER appuser

# Expose port and set command
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]