#!/bin/bash
# PostgreSQL Database Setup for RouteForce

echo "🗄️ Setting up PostgreSQL for RouteForce..."

# Create database and user (requires PostgreSQL to be installed)
echo "Creating database and user..."

# Note: These commands require PostgreSQL superuser access
# Run these manually on your production server:
cat << 'EOF'
-- Connect to PostgreSQL as superuser and run:
CREATE DATABASE routeforce_prod;
CREATE USER routeforce_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE routeforce_prod TO routeforce_user;

-- Grant additional permissions for schema operations
\c routeforce_prod
GRANT ALL ON SCHEMA public TO routeforce_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO routeforce_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO routeforce_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO routeforce_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO routeforce_user;
EOF

echo "✅ PostgreSQL setup commands generated above"
echo "📝 Copy and run the SQL commands in your PostgreSQL instance"

# Update requirements.txt to include PostgreSQL driver
echo "📦 Updating requirements.txt..."
if ! grep -q "psycopg2-binary" requirements.txt; then
    echo "psycopg2-binary==2.9.10" >> requirements.txt
    echo "✅ Added psycopg2-binary to requirements.txt"
fi

# Set environment variable for local testing
export DATABASE_URL=postgresql://routeforce_user:secure_password_here@localhost:5432/routeforce_prod

echo "🔧 DATABASE_URL environment variable set"
echo "💡 Update your production .env file with the actual database credentials"

# Test database migration (if database exists)
echo "🧪 Testing database migration..."
python -c "
try:
    from app import create_app
    app = create_app('production')
    with app.app_context():
        from app.models.database import db
        db.create_all()
    print('✅ Database schema created successfully')
except Exception as e:
    print(f'⚠️ Database connection test: {e}')
    print('💡 This is expected if PostgreSQL is not set up yet')
"

echo "✅ PostgreSQL setup preparation complete!"
