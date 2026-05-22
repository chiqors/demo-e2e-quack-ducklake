FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir duckdb==1.5.3
COPY query_worker.py /app/query_worker.py