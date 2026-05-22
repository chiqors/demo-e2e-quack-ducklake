import os
import time
import duckdb

print("Starting Quack Server with Postgres Metadata Catalog...")

pg_conn = os.getenv("PG_CONN")
s3_endpoint = os.getenv("S3_ENDPOINT")
s3_access_key = os.getenv("S3_ACCESS_KEY")
s3_secret_key = os.getenv("S3_SECRET_KEY")
s3_bucket = os.getenv("S3_BUCKET")

con = duckdb.connect(database=':memory:')

# Load networking, cloud object storage, and postgres extensions
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL postgres; LOAD postgres;")
con.execute("INSTALL quack; LOAD quack;")
con.execute("INSTALL ducklake; LOAD ducklake;")

# Configure a scoped S3 secret for MinIO-backed DuckLake data files.
con.execute(f"""
    CREATE OR REPLACE SECRET ducklake_s3 (
        TYPE s3,
        PROVIDER config,
        KEY_ID '{s3_access_key}',
        SECRET '{s3_secret_key}',
        REGION 'us-east-1',
        ENDPOINT '{s3_endpoint}',
        URL_STYLE 'path',
        USE_SSL false,
        SCOPE 's3://{s3_bucket}/'
    );
""")

print("Attaching DuckLake to Postgres Catalog and S3 storage layout...")
# Syntax maps directly to: ATTACH 'ducklake:postgres:<conn_string>' (DATA_PATH)
con.execute(f"""
    ATTACH 'ducklake:postgres:{pg_conn}' AS my_ducklake (
        DATA_PATH 's3://{s3_bucket}/my_ducklake_data/'
    );
""")
con.execute("USE my_ducklake;")

print("Exposing DuckLake architecture on port 9494 via quack_serve()...")
con.execute(
    "CALL quack_serve('quack:0.0.0.0:9494', token => 'secure_demo_token', allow_other_hostname => true);"
)

print("Server is up and routing metadata traffic to Postgres. Standing by...")
while True:
    time.sleep(3600)
