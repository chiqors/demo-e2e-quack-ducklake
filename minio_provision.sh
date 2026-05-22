#!/bin/sh
mc alias set local_lake http://minio:9000 minio_admin minio_secret_pass
mc mb --ignore-existing local_lake/healthcare-lake
echo "Storage bucket 'healthcare-lake' ready."
exit 0