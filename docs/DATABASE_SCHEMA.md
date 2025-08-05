# PostgreSQL Database Schema Documentation

## Overview

This document describes the PostgreSQL database schema for the RouteForce Routing application. The schema is designed to store user accounts, route data, store locations, optimization results, and analytics in a scalable and efficient manner.

## Database Tables

### Users Table

The `users` table stores user account information and authentication data.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    CONSTRAINT ck_users_role_valid CHECK (role IN ('admin', 'manager', 'user', 'driver'))
);
```

**Indexes:**
- `ix_users_email` - Performance index for email lookups
- `ix_users_username` - Performance index for username lookups
- `ix_users_role` - Index for role-based queries
- `ix_users_is_active` - Index for active user filtering
- `ix_users_created_at` - Index for temporal queries

**Fields:**
- `id`: Primary key, auto-incrementing
- `username`: Unique username for login
- `email`: Unique email address
- `password_hash`: Secure password hash (bcrypt)
- `first_name`, `last_name`: User's full name
- `role`: User role (admin, manager, user, driver)
- `is_active`: Account status flag
- `created_at`: Account creation timestamp
- `updated_at`: Last modification timestamp
- `last_login`: Last login timestamp

### Routes Table

The `routes` table stores route definitions and optimization results.

```sql
CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    description TEXT,
    route_data TEXT NOT NULL,  -- JSON string of route points
    total_distance FLOAT,
    estimated_time INTEGER,   -- Minutes
    optimization_score FLOAT,
    algorithm_used VARCHAR(50),
    status VARCHAR(20) DEFAULT 'generated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    
    CONSTRAINT ck_routes_status_valid CHECK (status IN ('generated', 'in_progress', 'completed', 'cancelled')),
    CONSTRAINT ck_routes_distance_positive CHECK (total_distance > 0),
    CONSTRAINT ck_routes_time_positive CHECK (estimated_time > 0)
);
```

**Indexes:**
- `ix_routes_user_id` - Foreign key index for user relationships
- `ix_routes_status` - Index for status filtering
- `ix_routes_algorithm_used` - Index for algorithm queries
- `ix_routes_created_at` - Index for temporal queries
- `ix_routes_total_distance` - Index for distance-based sorting

**Fields:**
- `id`: Primary key, auto-incrementing
- `name`: Human-readable route name
- `description`: Optional route description
- `route_data`: JSON string containing route points and sequence
- `total_distance`: Total route distance in kilometers
- `estimated_time`: Estimated time in minutes
- `optimization_score`: Algorithm optimization score (0-1)
- `algorithm_used`: Algorithm identifier used for optimization
- `status`: Route execution status
- `user_id`: Foreign key to users table

### Stores Table

The `stores` table contains store/location data for route planning.

```sql
CREATE TABLE stores (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address VARCHAR(500),
    latitude FLOAT,
    longitude FLOAT,
    chain VARCHAR(100),
    store_type VARCHAR(50),
    priority INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    store_metadata TEXT,  -- JSON string for additional data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    
    CONSTRAINT ck_stores_priority_valid CHECK (priority >= 1 AND priority <= 10),
    CONSTRAINT ck_stores_latitude_valid CHECK (latitude >= -90 AND latitude <= 90),
    CONSTRAINT ck_stores_longitude_valid CHECK (longitude >= -180 AND longitude <= 180)
);
```

**Indexes:**
- `ix_stores_user_id` - Foreign key index for user relationships
- `ix_stores_is_active` - Index for active store filtering
- `ix_stores_chain` - Index for chain-based queries
- `ix_stores_store_type` - Index for store type filtering
- `ix_stores_priority` - Index for priority-based sorting
- `ix_stores_coordinates` - Composite index for geospatial queries

**Fields:**
- `id`: Primary key, auto-incrementing
- `name`: Store name
- `address`: Full store address
- `latitude`, `longitude`: GPS coordinates
- `chain`: Store chain identifier
- `store_type`: Category of store
- `priority`: Visit priority (1-10 scale, 10 = highest)
- `is_active`: Store active status
- `store_metadata`: JSON string for additional store data
- `user_id`: Foreign key to users table

### Route Optimizations Table

The `route_optimizations` table tracks optimization algorithm performance and results.

```sql
CREATE TABLE route_optimizations (
    id SERIAL PRIMARY KEY,
    execution_time FLOAT NOT NULL,  -- Seconds
    algorithm VARCHAR(50) NOT NULL,
    parameters TEXT,  -- JSON string
    improvement_score FLOAT,
    original_distance FLOAT,
    optimized_distance FLOAT,
    stores_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    route_id INTEGER NOT NULL REFERENCES routes(id),
    user_id INTEGER REFERENCES users(id),
    
    CONSTRAINT ck_route_optimizations_execution_time_positive CHECK (execution_time >= 0),
    CONSTRAINT ck_route_optimizations_stores_count_positive CHECK (stores_count > 0)
);
```

**Indexes:**
- `ix_route_optimizations_route_id` - Foreign key index for route relationships
- `ix_route_optimizations_user_id` - Foreign key index for user relationships
- `ix_route_optimizations_algorithm` - Index for algorithm queries
- `ix_route_optimizations_created_at` - Index for temporal queries

**Fields:**
- `id`: Primary key, auto-incrementing
- `execution_time`: Algorithm execution time in seconds
- `algorithm`: Algorithm identifier
- `parameters`: JSON string of algorithm parameters
- `improvement_score`: Percentage improvement over baseline
- `original_distance`: Distance before optimization
- `optimized_distance`: Distance after optimization
- `stores_count`: Number of stores in the route
- `route_id`: Foreign key to routes table
- `user_id`: Foreign key to users table

### Analytics Table

The `analytics` table stores usage analytics and system events.

```sql
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_data TEXT,  -- JSON string
    user_id INTEGER REFERENCES users(id),
    session_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `ix_analytics_user_id` - Foreign key index for user relationships
- `ix_analytics_event_type` - Index for event type filtering
- `ix_analytics_created_at` - Index for temporal queries
- `ix_analytics_session_id` - Index for session-based queries

**Fields:**
- `id`: Primary key, auto-incrementing
- `event_type`: Type of event (e.g., 'route_generated', 'user_login')
- `event_data`: JSON string containing event details
- `user_id`: Foreign key to users table
- `session_id`: Session identifier
- `ip_address`: Client IP address
- `user_agent`: Client user agent string
- `created_at`: Event timestamp

## Relationships

### User Relationships

- **One-to-Many**: User → Routes (user_id foreign key)
- **One-to-Many**: User → Stores (user_id foreign key)
- **One-to-Many**: User → Route Optimizations (user_id foreign key)
- **One-to-Many**: User → Analytics (user_id foreign key)

### Route Relationships

- **Many-to-One**: Routes → User (user_id foreign key)
- **One-to-Many**: Route → Route Optimizations (route_id foreign key)

## Data Integrity Features

### Check Constraints

1. **User Role Validation**: Ensures role is one of valid values
2. **Route Status Validation**: Ensures status is one of valid values
3. **Store Priority Range**: Ensures priority is between 1-10
4. **Positive Values**: Ensures distances and times are positive
5. **Coordinate Bounds**: Ensures latitude/longitude are within valid ranges
6. **Algorithm Metrics**: Ensures execution times and store counts are positive

### Foreign Key Constraints

- All foreign key relationships enforce referential integrity
- Cascading deletes are not implemented to preserve data integrity
- NULL values are allowed for optional relationships

### Indexes

- **Performance Indexes**: On commonly queried fields
- **Foreign Key Indexes**: On all foreign key columns
- **Composite Indexes**: For multi-column queries (e.g., coordinates)
- **Temporal Indexes**: On timestamp fields for time-based queries

## Performance Considerations

### Query Optimization

1. **User Queries**: Indexed on email, username, role, and active status
2. **Route Queries**: Indexed on user, status, algorithm, and creation date
3. **Store Queries**: Indexed on user, active status, chain, type, and coordinates
4. **Analytics Queries**: Indexed on user, event type, session, and creation date

### Geospatial Queries

- Composite index on (latitude, longitude) for proximity searches
- Consider PostGIS extension for advanced geospatial operations

### Scaling Recommendations

1. **Partitioning**: Consider date-based partitioning for analytics table
2. **Archiving**: Implement data archiving strategy for old records
3. **Connection Pooling**: Use connection pooling for high-concurrency scenarios
4. **Read Replicas**: Consider read replicas for reporting and analytics

## Migration History

- **Initial Migration** (`cbeacf70ea5a`): Created base tables and relationships
- **Schema Enhancement** (`f2fdd197ed5c`): Added indexes, constraints, and data validation

## Best Practices

### Data Access

1. Always use parameterized queries to prevent SQL injection
2. Use appropriate indexes for query patterns
3. Implement proper connection pooling
4. Monitor query performance and optimize as needed

### Data Integrity

1. Validate data at application level before database insertion
2. Use database constraints as a safety net
3. Implement proper error handling for constraint violations
4. Regular backup and recovery testing

### Security

1. Use environment variables for database credentials
2. Implement proper authentication and authorization
3. Regular security audits and updates
4. Encrypt sensitive data at rest and in transit