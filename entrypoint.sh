#!/bin/sh

if [ ! -f "certs/jwt-private.pem" ]; then
    echo "JWT keys not found. Generating..."
    mkdir -p certs
    openssl genpkey -algorithm RSA -out certs/jwt-private.pem -pkeyopt rsa_keygen_bits:2048
    openssl rsa -pubout -in certs/jwt-private.pem -out certs/jwt-public.pem
    chmod 600 certs/jwt-private.pem certs/jwt-public.pem
fi


if echo "$DB_URL" | grep -q "sqlite"; then
    echo "SQLite database detected. Skipping port wait..."
else
    echo "Waiting for PostgreSQL database to be ready..."
    python -c "
import socket
import time
import os
from urllib.parse import urlparse

db_url = os.getenv('DB_URL', '')
parsed = urlparse(db_url)
host = parsed.hostname or 'db'
port = parsed.port or 5432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect((host, port))
        s.close()
        break
    except socket.error:
        time.sleep(0.5)
"
    echo "Database is ready!"
fi

echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000