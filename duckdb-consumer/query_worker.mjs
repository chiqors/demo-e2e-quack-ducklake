import duckdb from '@duckdb/node-api';

const quackHost = process.env.QUACK_HOST;

if (!quackHost) {
  throw new Error('QUACK_HOST is required');
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

console.log('Starting Consumer Client Node...');

const instance = await duckdb.DuckDBInstance.create(':memory:');
const connection = await instance.connect();

await connection.run('INSTALL quack; LOAD quack;');

console.log(`Connecting to Quack wire mesh network at ${quackHost}...`);
await connection.run(
  `ATTACH 'quack:${quackHost}' AS remote_lake (TOKEN 'secure_demo_token', DISABLE_SSL true);`
);

console.log('Creating table through Quack (will log to Postgres, write to S3)...');
await connection.run(`
  FROM remote_lake.query(
    'CREATE TABLE IF NOT EXISTS my_ducklake.main.orders (
      id INTEGER,
      product VARCHAR,
      total DOUBLE
    )'
  );
`);

console.log('Executing INSERT data stream...');
await connection.run(
  `FROM remote_lake.query("INSERT INTO my_ducklake.main.orders VALUES (101, 'Premium Widget', 149.99)");`
);

console.log('Validating E2E snapshot recovery query...');
const reader = await connection.runAndReadAll(
  `FROM remote_lake.query('SELECT * FROM my_ducklake.main.orders ORDER BY id');`
);
const rows = reader.getRows();

console.log('\n--- TEST ROW RETRIEVED FROM DATA LAKE ---');
for (const row of rows) {
  console.log(`Order ID: ${row[0]} | Item: ${row[1]} | Cost: $${row[2]}`);
}
console.log('-----------------------------------------\n');

while (true) {
  await sleep(3600_000);
}
