-- HT Status Database Initialization
-- This script runs when PostgreSQL container starts for the first time

-- Create test database for automated testing
-- Only create if it doesn't exist to avoid errors on restart
SELECT 'CREATE DATABASE htplanner_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'htplanner_test')\gexec

-- Grant privileges to htstatus user
GRANT ALL PRIVILEGES ON DATABASE htplanner TO htstatus;
GRANT ALL PRIVILEGES ON DATABASE htplanner_test TO htstatus;

-- Connect to main database and set up any initial data
\c htplanner;

-- Enable extensions that might be needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Connect to test database and set up same extensions
\c htplanner_test;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
