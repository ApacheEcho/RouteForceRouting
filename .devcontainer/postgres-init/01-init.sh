#!/bin/bash
set -e

# Create additional databases for testing and development
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create test database
    CREATE DATABASE routeforce_test;
    GRANT ALL PRIVILEGES ON DATABASE routeforce_test TO routeforce;

    -- Create staging database
    CREATE DATABASE routeforce_staging;
    GRANT ALL PRIVILEGES ON DATABASE routeforce_staging TO routeforce;

    -- Install extensions
    \c routeforce_dev;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "postgis" CASCADE;
    
    \c routeforce_test;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "postgis" CASCADE;
    
    \c routeforce_staging;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "postgis" CASCADE;
EOSQL

echo "PostgreSQL initialization completed!"
echo "Created databases:"
echo "  - routeforce_dev (development)"
echo "  - routeforce_test (testing)"  
echo "  - routeforce_staging (staging)"
echo "Installed extensions: uuid-ossp, postgis"
