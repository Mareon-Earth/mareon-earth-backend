# 1. Base Image: Use a specific Python version for reproducibility
FROM python

# 2. Set Environment Variables to improve container behavior
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Make scripts executable
RUN chmod +x scripts/*.sh

# 7. Expose the port the app runs on
# The PORT env var is automatically set by Cloud Run, and run.sh uses it.
EXPOSE 8000

# 8. Default command to run the application (can be overridden by Cloud Run)
CMD ["./scripts/run.sh"]