FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN python -m venv venv
RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src ./src

# Set environment variables (example)
ENV APP_NAME="Global Welfare Monitor"
ENV DATA_DIR="/data"

# Create data directory
RUN mkdir -p ${DATA_DIR}

# Expose the FastAPI port
EXPOSE 8000

# Define health check (example - adjust to your app)
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Command to run the FastAPI application
CMD ["./src/run_api.sh"]
