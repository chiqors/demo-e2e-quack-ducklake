import duckdb from '@duckdb/node-api';

const instance = await duckdb.DuckDBInstance.create(':memory:');
const connection = await instance.connect();

await connection.run('INSTALL quack; LOAD quack;');
await connection.run(
  "ATTACH 'quack:quack-server:9494' AS remote_lake (TOKEN 'secure_demo_token', DISABLE_SSL true);"
);

await connection.run("FROM remote_lake.query('DELETE FROM my_ducklake.main.orders');");
await connection.run(`
  FROM remote_lake.query(
    "INSERT INTO my_ducklake.main.orders
     SELECT i, 'bulk-widget-' || i::VARCHAR, i * 1.25
     FROM range(1, 50001) t(i)"
  );
`);

const reader = await connection.runAndReadAll(
  "FROM remote_lake.query('SELECT COUNT(*)::INTEGER, MIN(id), MAX(id) FROM my_ducklake.main.orders');"
);

for (const row of reader.getRowsJS()) {
  console.log(`count=${row[0]} min_id=${row[1]} max_id=${row[2]}`);
}
