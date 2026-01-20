#!/bin/bash
# Wait for PostgreSQL to be ready
# Usage: ./wait-for-postgres.sh [host] [port] [user] [database]

set -e

host="${1:-localhost}"
port="${2:-5432}"
user="${3:-htstatus}"
database="${4:-htplanner}"

echo "Waiting for PostgreSQL at $host:$port..."

until pg_isready -h "$host" -p "$port" -U "$user" -d "$database" &> /dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing command"
