import os
import time
import duckdb

print("Starting Consumer Client Node...")
quack_host = os.getenv("QUACK_HOST")

con = duckdb.connect(database=':memory:')
con.execute("INSTALL quack; LOAD quack;")

print(f"Connecting to Quack wire mesh network at {quack_host}...")
con.execute(
    f"ATTACH 'quack:{quack_host}' AS remote_lake (TOKEN 'secure_demo_token', DISABLE_SSL true);"
)

print("Creating table through Quack (will log to Postgres, write to S3)...")
con.execute("""
    FROM remote_lake.query(
        'CREATE TABLE IF NOT EXISTS my_ducklake.main.orders (
            id INTEGER,
            product VARCHAR,
            total DOUBLE
        )'
    );
""")

print("Executing INSERT data stream...")
con.execute(
    "FROM remote_lake.query(\"INSERT INTO my_ducklake.main.orders VALUES (101, 'Premium Widget', 149.99)\");"
)

print("Validating E2E snapshot recovery query...")
res = con.execute(
    "FROM remote_lake.query('SELECT * FROM my_ducklake.main.orders ORDER BY id');"
).fetchall()

print("\n--- TEST ROW RETRIEVED FROM DATA LAKE ---")
for row in res:
    print(f"Order ID: {row[0]} | Item: {row[1]} | Cost: ${row[2]}")
print("-----------------------------------------\n")

while True:
    time.sleep(3600)
