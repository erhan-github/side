# Multi-stage build for side-backend
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt


# Final Stage
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache /wheels/*

# Copy Source Code
COPY src/ src/
COPY run_server.py .

# Environment Variables
ENV PYTHONPATH=/app/src

# Non-root user
RUN useradd -m sideuser && chown -R sideuser:sideuser /app
USER sideuser

# Healthcheck - Railway assigns port 8080 by default
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Graceful shutdown signal
STOPSIGNAL SIGTERM

CMD ["python", "run_server.py"]
