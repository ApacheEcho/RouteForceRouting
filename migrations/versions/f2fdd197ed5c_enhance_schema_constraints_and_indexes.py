"""enhance_schema_constraints_and_indexes

Revision ID: f2fdd197ed5c
Revises: cbeacf70ea5a
Create Date: 2025-08-05 17:03:37.318112

Adds database constraints, indexes, and enhancements for better performance and data integrity:
- Performance indexes on commonly queried fields
- Check constraints for data validation
- Enhanced foreign key relationships
- Optimized query patterns for route and user data
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2fdd197ed5c'
down_revision = 'cbeacf70ea5a'
branch_labels = None
depends_on = None


def upgrade():
    # Add performance indexes for users table
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], unique=False)
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    
    # Add performance indexes for routes table
    op.create_index(op.f('ix_routes_user_id'), 'routes', ['user_id'], unique=False)
    op.create_index(op.f('ix_routes_status'), 'routes', ['status'], unique=False)
    op.create_index(op.f('ix_routes_algorithm_used'), 'routes', ['algorithm_used'], unique=False)
    op.create_index(op.f('ix_routes_created_at'), 'routes', ['created_at'], unique=False)
    op.create_index(op.f('ix_routes_total_distance'), 'routes', ['total_distance'], unique=False)
    
    # Add performance indexes for stores table
    op.create_index(op.f('ix_stores_user_id'), 'stores', ['user_id'], unique=False)
    op.create_index(op.f('ix_stores_is_active'), 'stores', ['is_active'], unique=False)
    op.create_index(op.f('ix_stores_chain'), 'stores', ['chain'], unique=False)
    op.create_index(op.f('ix_stores_store_type'), 'stores', ['store_type'], unique=False)
    op.create_index(op.f('ix_stores_priority'), 'stores', ['priority'], unique=False)
    # Geospatial index for location queries
    op.create_index(op.f('ix_stores_coordinates'), 'stores', ['latitude', 'longitude'], unique=False)
    
    # Add performance indexes for route_optimizations table
    op.create_index(op.f('ix_route_optimizations_route_id'), 'route_optimizations', ['route_id'], unique=False)
    op.create_index(op.f('ix_route_optimizations_user_id'), 'route_optimizations', ['user_id'], unique=False)
    op.create_index(op.f('ix_route_optimizations_algorithm'), 'route_optimizations', ['algorithm'], unique=False)
    op.create_index(op.f('ix_route_optimizations_created_at'), 'route_optimizations', ['created_at'], unique=False)
    
    # Add performance indexes for analytics table
    op.create_index(op.f('ix_analytics_user_id'), 'analytics', ['user_id'], unique=False)
    op.create_index(op.f('ix_analytics_event_type'), 'analytics', ['event_type'], unique=False)
    op.create_index(op.f('ix_analytics_created_at'), 'analytics', ['created_at'], unique=False)
    op.create_index(op.f('ix_analytics_session_id'), 'analytics', ['session_id'], unique=False)
    
    # Add check constraints for data validation
    # User role validation
    op.create_check_constraint(
        'ck_users_role_valid',
        'users',
        "role IN ('admin', 'manager', 'user', 'driver')"
    )
    
    # Route status validation
    op.create_check_constraint(
        'ck_routes_status_valid',
        'routes',
        "status IN ('generated', 'in_progress', 'completed', 'cancelled')"
    )
    
    # Store priority validation (1-10 scale)
    op.create_check_constraint(
        'ck_stores_priority_valid',
        'stores',
        'priority >= 1 AND priority <= 10'
    )
    
    # Distance and time validation (must be positive)
    op.create_check_constraint(
        'ck_routes_distance_positive',
        'routes',
        'total_distance > 0'
    )
    
    op.create_check_constraint(
        'ck_routes_time_positive',
        'routes',
        'estimated_time > 0'
    )
    
    # Coordinate validation (basic latitude/longitude bounds)
    op.create_check_constraint(
        'ck_stores_latitude_valid',
        'stores',
        'latitude >= -90 AND latitude <= 90'
    )
    
    op.create_check_constraint(
        'ck_stores_longitude_valid',
        'stores',
        'longitude >= -180 AND longitude <= 180'
    )
    
    # Optimization metrics validation
    op.create_check_constraint(
        'ck_route_optimizations_execution_time_positive',
        'route_optimizations',
        'execution_time >= 0'
    )
    
    op.create_check_constraint(
        'ck_route_optimizations_stores_count_positive',
        'route_optimizations',
        'stores_count > 0'
    )


def downgrade():
    # Remove check constraints
    op.drop_constraint('ck_route_optimizations_stores_count_positive', 'route_optimizations', type_='check')
    op.drop_constraint('ck_route_optimizations_execution_time_positive', 'route_optimizations', type_='check')
    op.drop_constraint('ck_stores_longitude_valid', 'stores', type_='check')
    op.drop_constraint('ck_stores_latitude_valid', 'stores', type_='check')
    op.drop_constraint('ck_routes_time_positive', 'routes', type_='check')
    op.drop_constraint('ck_routes_distance_positive', 'routes', type_='check')
    op.drop_constraint('ck_stores_priority_valid', 'stores', type_='check')
    op.drop_constraint('ck_routes_status_valid', 'routes', type_='check')
    op.drop_constraint('ck_users_role_valid', 'users', type_='check')
    
    # Remove indexes
    op.drop_index(op.f('ix_analytics_session_id'), table_name='analytics')
    op.drop_index(op.f('ix_analytics_created_at'), table_name='analytics')
    op.drop_index(op.f('ix_analytics_event_type'), table_name='analytics')
    op.drop_index(op.f('ix_analytics_user_id'), table_name='analytics')
    
    op.drop_index(op.f('ix_route_optimizations_created_at'), table_name='route_optimizations')
    op.drop_index(op.f('ix_route_optimizations_algorithm'), table_name='route_optimizations')
    op.drop_index(op.f('ix_route_optimizations_user_id'), table_name='route_optimizations')
    op.drop_index(op.f('ix_route_optimizations_route_id'), table_name='route_optimizations')
    
    op.drop_index(op.f('ix_stores_coordinates'), table_name='stores')
    op.drop_index(op.f('ix_stores_priority'), table_name='stores')
    op.drop_index(op.f('ix_stores_store_type'), table_name='stores')
    op.drop_index(op.f('ix_stores_chain'), table_name='stores')
    op.drop_index(op.f('ix_stores_is_active'), table_name='stores')
    op.drop_index(op.f('ix_stores_user_id'), table_name='stores')
    
    op.drop_index(op.f('ix_routes_total_distance'), table_name='routes')
    op.drop_index(op.f('ix_routes_created_at'), table_name='routes')
    op.drop_index(op.f('ix_routes_algorithm_used'), table_name='routes')
    op.drop_index(op.f('ix_routes_status'), table_name='routes')
    op.drop_index(op.f('ix_routes_user_id'), table_name='routes')
    
    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
