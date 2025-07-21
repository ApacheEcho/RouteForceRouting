-- RouteForce Production Database Initialization
-- Create extensions and initial schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schema for multi-tenant support
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Set search path
SET search_path TO public, analytics, monitoring;

-- Create admin user with appropriate permissions
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'routeforce_admin') THEN
      CREATE USER routeforce_admin WITH PASSWORD 'admin_secure_2024';
   END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE routeforce TO routeforce_admin;
GRANT ALL PRIVILEGES ON SCHEMA public TO routeforce_admin;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO routeforce_admin;
GRANT ALL PRIVILEGES ON SCHEMA monitoring TO routeforce_admin;

-- Create initial tables structure (will be managed by SQLAlchemy migrations)
-- This is just for reference, actual tables created by Flask-Migrate

-- Users and Organizations (Multi-tenant)
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    plan VARCHAR(50) DEFAULT 'basic',
    max_users INTEGER DEFAULT 10,
    max_routes INTEGER DEFAULT 1000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Routes and Optimization Data
CREATE TABLE IF NOT EXISTS routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    start_location VARCHAR(255),
    end_location VARCHAR(255),
    waypoints JSONB,
    optimization_type VARCHAR(50),
    optimization_parameters JSONB,
    results JSONB,
    distance_km DECIMAL(10,2),
    duration_minutes INTEGER,
    fuel_consumption DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics and Performance Data
CREATE TABLE IF NOT EXISTS analytics.route_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metrics JSONB NOT NULL,
    ml_predictions JSONB,
    performance_score DECIMAL(5,2)
);

-- Monitoring and System Health
CREATE TABLE IF NOT EXISTS monitoring.system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4),
    metadata JSONB,
    instance_id VARCHAR(100)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_organizations_subdomain ON organizations(subdomain);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_organization ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_routes_organization ON routes(organization_id);
CREATE INDEX IF NOT EXISTS idx_routes_created_at ON routes(created_at);
CREATE INDEX IF NOT EXISTS idx_analytics_route_performance_timestamp ON analytics.route_performance(timestamp);
CREATE INDEX IF NOT EXISTS idx_analytics_route_performance_route ON analytics.route_performance(route_id);
CREATE INDEX IF NOT EXISTS idx_monitoring_system_metrics_timestamp ON monitoring.system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_monitoring_system_metrics_type ON monitoring.system_metrics(metric_type);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_routes_waypoints_gin ON routes USING GIN(waypoints);
CREATE INDEX IF NOT EXISTS idx_routes_results_gin ON routes USING GIN(results);
CREATE INDEX IF NOT EXISTS idx_analytics_metrics_gin ON analytics.route_performance USING GIN(metrics);
CREATE INDEX IF NOT EXISTS idx_monitoring_metadata_gin ON monitoring.system_metrics USING GIN(metadata);

-- Create trigger for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to tables
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON routes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default organization and admin user
INSERT INTO organizations (id, name, subdomain, plan, max_users, max_routes) 
VALUES (
    uuid_generate_v4(),
    'RouteForce Demo',
    'demo',
    'enterprise',
    100,
    10000
) ON CONFLICT DO NOTHING;

-- Performance optimization settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET track_activity_query_size = 2048;
ALTER SYSTEM SET log_min_duration_statement = 1000;

-- Vacuum and analyze for better performance
VACUUM ANALYZE;
