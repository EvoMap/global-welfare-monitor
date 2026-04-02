FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

COPY src ./src

ENV APP_NAME="Global Welfare Monitor"
ENV DATA_DIR="/data"
ENV PATH="/app/venv/bin:$PATH"

RUN mkdir -p ${DATA_DIR}

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["./src/run_api.sh"]
