# 1. Base Image: Use the latest stable Python 3.14 slim image
FROM python:3.14-slim

# 2. Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Pip configuration
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# 3. System Dependencies
# Install curl/netcat for healthchecks if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. Create a non-root user
RUN addgroup --system app && adduser --system --group app

# 5. Set working directory
WORKDIR /app

# 6. Install dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# 7. Copy application code
COPY . .

# 8. Permission handling
# Make scripts executable and change ownership to non-root user
RUN chmod +x scripts/*.sh && \
    chown -R app:app /app

# 9. Switch to non-root user
USER app

# 10. Expose port (Documentation only; Cloud Run handles mapping)
EXPOSE 8000

# 11. Run
CMD ["./scripts/run.sh"]