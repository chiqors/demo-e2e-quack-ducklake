FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir duckdb==1.5.3
COPY server_init.py /app/server_init.py
CMD ["python", "/app/server_init.py"]