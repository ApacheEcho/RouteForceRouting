from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging
import time

logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    """Enterprise-grade database connection pooling"""
    
    def __init__(self, database_url, pool_size=20, max_overflow=40):
        """Initialize connection pool with monitoring"""
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        
        # Create engine with connection pooling
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=30,
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_pre_ping=True,  # Verify connections before use
            echo_pool=True  # Enable pool logging
        )
        
        # Monitoring metrics
        self.connection_metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'failed_connections': 0,
            'average_connection_time': 0
        }
        
        logger.info(f"Database connection pool initialized: size={pool_size}, overflow={max_overflow}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for safe connection handling"""
        conn = None
        start_time = time.time()
        
        try:
            # Get connection from pool
            conn = self.engine.connect()
            self.connection_metrics['total_connections'] += 1
            self.connection_metrics['active_connections'] += 1
            
            yield conn
            
        except Exception as e:
            self.connection_metrics['failed_connections'] += 1
            logger.error(f"Database connection error: {e}")
            
            if conn:
                conn.rollback()
            raise
            
        finally:
            # Update metrics
            connection_time = time.time() - start_time
            self._update_average_connection_time(connection_time)
            
            if conn:
                self.connection_metrics['active_connections'] -= 1
                conn.close()
    
    def health_check(self):
        """Check database connection health"""
        try:
            with self.get_connection() as conn:
                result = conn.execute("SELECT 1")
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_pool_status(self):
        """Get current pool status and metrics"""
        pool = self.engine.pool
        
        return {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'total': pool.total(),
            'metrics': self.connection_metrics
        }
    
    def _update_average_connection_time(self, new_time):
        """Update rolling average of connection time"""
        current_avg = self.connection_metrics['average_connection_time']
        total_conns = self.connection_metrics['total_connections']
        
        if total_conns == 1:
            self.connection_metrics['average_connection_time'] = new_time
        else:
            # Calculate new average
            new_avg = ((current_avg * (total_conns - 1)) + new_time) / total_conns
            self.connection_metrics['average_connection_time'] = new_avg
    
    def close_all_connections(self):
        """Close all connections in the pool"""
        self.engine.dispose()
        logger.info("All database connections closed")
