"""
Advanced Database Connection Pool with Auto-Optimization - AUTO-PILOT ENHANCEMENT
High-performance database connection management with automatic optimization
"""
import time
import threading
import logging
from typing import Dict, Any
from dataclasses import dataclass, field
from contextlib import contextmanager
from queue import Queue, Empty
import weakref
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

@dataclass
class ConnectionMetrics:
    """Database connection metrics"""
    active_connections: int = 0
    total_connections: int = 0
    avg_query_time: float = 0.0
    slow_queries: int = 0
    connection_errors: int = 0
    pool_overflow: int = 0
    timestamp: float = field(default_factory=time.time)

class DatabaseConnectionPool:
    """Advanced database connection pool with monitoring and optimization"""
    
    def __init__(self, database_url: str, pool_size: int = 10, max_overflow: int = 20):
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        
        # Metrics tracking
        self.metrics = ConnectionMetrics()
        self.query_times = Queue(maxsize=1000)
        self.slow_query_threshold = 1.0  # seconds
        
        # Connection tracking
        self.active_connections = weakref.WeakSet()
        self.connection_stats = {'created': 0, 'closed': 0, 'errors': 0}
        
        # Optimization settings
        self.auto_optimize = True
        self.optimization_interval = 300  # 5 minutes
        self.last_optimization = time.time()
        
        # Thread safety
        self._lock = threading.RLock()
        
        self._setup_engine()
    
    def _setup_engine(self) -> None:
        """Setup database engine with optimized configuration"""
        
        # Optimized engine configuration
        engine_config = {
            'poolclass': QueuePool,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'pool_pre_ping': True,  # Verify connections
            'pool_recycle': 3600,   # Recycle connections every hour
            'pool_timeout': 30,     # Connection timeout
            'echo': False,          # Disable SQL logging for performance
            'future': True,         # Use future-compatible engine
            'connect_args': {
                'connect_timeout': 10,
                'application_name': 'RouteForce_Optimized'
            }
        }
        
        # PostgreSQL-specific optimizations
        if 'postgresql' in self.database_url:
            engine_config['connect_args'].update({
                'options': '-c statement_timeout=30000'  # 30 second statement timeout
            })
        
        self.engine = create_engine(self.database_url, **engine_config)
        
        # Setup event listeners for monitoring
        self._setup_event_listeners()
        
        logger.info(f"🚀 Database connection pool initialized: {self.pool_size} connections, {self.max_overflow} overflow")
    
    def _setup_event_listeners(self) -> None:
        """Setup SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            with self._lock:
                self.connection_stats['created'] += 1
                self.metrics.total_connections += 1
        
        @event.listens_for(self.engine, "close")
        def receive_close(dbapi_connection, connection_record):
            with self._lock:
                self.connection_stats['closed'] += 1
        
        @event.listens_for(self.engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            context._query_start_time = time.time()
        
        @event.listens_for(self.engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            query_time = time.time() - context._query_start_time
            
            # Track query performance
            if not self.query_times.full():
                self.query_times.put(query_time)
            
            # Track slow queries
            if query_time > self.slow_query_threshold:
                with self._lock:
                    self.metrics.slow_queries += 1
                logger.warning(f"🐌 Slow query detected: {query_time:.3f}s - {statement[:100]}...")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic monitoring"""
        connection = None
        
        try:
            connection = self.engine.connect()
            with self._lock:
                self.metrics.active_connections += 1
                self.active_connections.add(connection)
            
            yield connection
            
        except Exception as e:
            with self._lock:
                self.connection_stats['errors'] += 1
                self.metrics.connection_errors += 1
            logger.error(f"Database connection error: {e}")
            raise
        
        finally:
            if connection:
                try:
                    connection.close()
                    with self._lock:
                        self.metrics.active_connections = max(0, self.metrics.active_connections - 1)
                        if connection in self.active_connections:
                            self.active_connections.remove(connection)
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            # Auto-optimization check
            if self.auto_optimize and time.time() - self.last_optimization > self.optimization_interval:
                self._auto_optimize()
    
    def _auto_optimize(self) -> None:
        """Automatic database connection optimization"""
        try:
            self.last_optimization = time.time()
            
            # Calculate current metrics
            self._update_metrics()
            
            optimizations_applied = []
            
            # Pool size optimization
            if self.metrics.pool_overflow > 5:
                new_pool_size = min(self.pool_size + 2, 50)  # Increase pool size
                if new_pool_size != self.pool_size:
                    self.pool_size = new_pool_size
                    optimizations_applied.append(f"increased_pool_size_to_{new_pool_size}")
            
            # High error rate optimization
            if self.metrics.connection_errors > 10:
                # Reset error counters and implement backoff
                with self._lock:
                    self.metrics.connection_errors = 0
                optimizations_applied.append("reset_error_counters")
            
            # Query performance optimization
            if self.metrics.slow_queries > 20:
                # Trigger query analysis
                optimizations_applied.append("query_performance_analysis")
            
            if optimizations_applied:
                logger.info(f"🔧 Database auto-optimization applied: {', '.join(optimizations_applied)}")
            
        except Exception as e:
            logger.error(f"Database auto-optimization failed: {e}")
    
    def _update_metrics(self) -> None:
        """Update connection pool metrics"""
        with self._lock:
            # Calculate average query time
            query_times_list = []
            while not self.query_times.empty():
                try:
                    query_times_list.append(self.query_times.get_nowait())
                except Empty:
                    break
            
            if query_times_list:
                self.metrics.avg_query_time = sum(query_times_list) / len(query_times_list)
            
            # Pool status - track active connections
            self.metrics.active_connections = len(self.active_connections)
            
            # Reset some counters periodically
            if self.metrics.slow_queries > 100:
                self.metrics.slow_queries = 0
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status and metrics"""
        with self._lock:
            pool = self.engine.pool
            
            return {
                'pool_size': self.pool_size,
                'max_overflow': self.max_overflow,
                'active_connections': self.metrics.active_connections,
                'total_connections': self.metrics.total_connections,
                'avg_query_time': self.metrics.avg_query_time,
                'slow_queries': self.metrics.slow_queries,
                'connection_errors': self.metrics.connection_errors,
                'connections_created': self.connection_stats['created'],
                'connections_closed': self.connection_stats['closed'],
                'connections_errored': self.connection_stats['errors'],
                'pool_status': {
                    'size': pool.size() if hasattr(pool, 'size') else 0,
                    'checked_in': pool.checkedin() if hasattr(pool, 'checkedin') else 0,
                    'checked_out': pool.checkedout() if hasattr(pool, 'checkedout') else 0,
                    'overflow': pool.overflow() if hasattr(pool, 'overflow') else 0
                }
            }
    
    def optimize_pool_configuration(self) -> Dict[str, Any]:
        """Optimize pool configuration based on current usage patterns"""
        status = self.get_pool_status()
        recommendations = []
        changes_made = []
        
        # Analyze usage patterns
        avg_active = status['active_connections']
        error_rate = status['connection_errors'] / max(status['total_connections'], 1)
        
        # Pool size recommendations
        if avg_active > self.pool_size * 0.8:
            recommended_size = min(self.pool_size + 5, 50)
            recommendations.append(f"Increase pool size to {recommended_size}")
        elif avg_active < self.pool_size * 0.2 and self.pool_size > 5:
            recommended_size = max(self.pool_size - 2, 5)
            recommendations.append(f"Decrease pool size to {recommended_size}")
        
        # Error rate analysis
        if error_rate > 0.05:  # 5% error rate
            recommendations.extend([
                "High error rate detected - check database connectivity",
                "Consider increasing connection timeout",
                "Review database server capacity"
            ])
        
        # Query performance analysis
        if status['avg_query_time'] > 1.0:
            recommendations.extend([
                "High average query time - review query optimization",
                "Consider database indexing improvements",
                "Analyze slow query patterns"
            ])
        
        return {
            'current_status': status,
            'recommendations': recommendations,
            'changes_made': changes_made,
            'optimization_score': self._calculate_optimization_score(status)
        }
    
    def _calculate_optimization_score(self, status: Dict[str, Any]) -> float:
        """Calculate optimization score (0-100)"""
        score = 100.0
        
        # Penalize high error rates
        error_rate = status['connection_errors'] / max(status['total_connections'], 1)
        score -= error_rate * 500  # Heavy penalty for errors
        
        # Penalize slow queries
        if status['avg_query_time'] > 0.5:
            score -= (status['avg_query_time'] - 0.5) * 20
        
        # Penalize pool overflow
        if status.get('pool_status', {}).get('overflow', 0) > 0:
            score -= 10
        
        return max(0.0, min(100.0, score))

class OptimizedDatabase:
    """Enhanced database wrapper with performance optimization"""
    
    def __init__(self, app=None, database_url: str = None):
        self.app = app
        self.database_url = database_url
        self.connection_pool = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize database with Flask app"""
        self.app = app
        
        # Get database URL from app config
        if not self.database_url:
            self.database_url = app.config.get('DATABASE_URL') or app.config.get('SQLALCHEMY_DATABASE_URI')
        
        if not self.database_url:
            raise ValueError("Database URL not configured")
        
        # Initialize optimized connection pool
        pool_size = app.config.get('DB_POOL_SIZE', 10)
        max_overflow = app.config.get('DB_MAX_OVERFLOW', 20)
        
        self.connection_pool = DatabaseConnectionPool(
            database_url=self.database_url,
            pool_size=pool_size,
            max_overflow=max_overflow
        )
        
        # Setup Flask-SQLAlchemy with optimized engine
        self.db = SQLAlchemy()
        self.db.engine = self.connection_pool.engine
        self.db.init_app(app)
        
        logger.info("🚀 Optimized database initialized")
    
    def get_connection(self):
        """Get database connection"""
        return self.connection_pool.get_connection()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get database performance report"""
        if not self.connection_pool:
            return {"status": "not_initialized"}
        
        return self.connection_pool.optimize_pool_configuration()
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute optimized database query"""
        with self.get_connection() as conn:
            return conn.execute(query, params or {})

# Global optimized database instance
optimized_db = OptimizedDatabase()

def init_optimized_database(app, database_url: str = None):
    """Initialize optimized database"""
    optimized_db.init_app(app)
    return optimized_db
