"""
Optimized Database Connection Pool - Beast Mode Enhancement
High-performance database connection management with intelligent pooling
"""

import time
import logging
import threading
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
import psycopg2
from psycopg2 import pool, sql
from flask import current_app
import sqlalchemy as sa
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool, StaticPool

logger = logging.getLogger(__name__)


@dataclass
class PoolMetrics:
    """Database connection pool metrics"""
    
    connections_created: int = 0
    connections_closed: int = 0
    connections_active: int = 0
    connections_idle: int = 0
    connections_invalid: int = 0
    connections_checked_out: int = 0
    pool_overflows: int = 0
    avg_checkout_time: float = 0.0
    avg_query_time: float = 0.0
    total_queries: int = 0
    failed_queries: int = 0
    timestamp: float = field(default_factory=time.time)
    
    def utilization_rate(self) -> float:
        """Calculate connection pool utilization"""
        total = self.connections_active + self.connections_idle
        return self.connections_active / total if total > 0 else 0.0
    
    def error_rate(self) -> float:
        """Calculate query error rate"""
        return self.failed_queries / self.total_queries if self.total_queries > 0 else 0.0
    
    def performance_score(self) -> float:
        """Calculate pool performance score (0-100)"""
        utilization = self.utilization_rate()
        error_rate = self.error_rate()
        
        # Optimal utilization is around 60-80%
        utilization_score = 100 - abs(70 - utilization * 100)
        error_penalty = error_rate * 200  # Heavy penalty for errors
        overflow_penalty = self.pool_overflows * 10
        
        score = utilization_score - error_penalty - overflow_penalty
        return max(0.0, min(100.0, score))


class OptimizedConnectionPool:
    """Advanced database connection pool with Beast Mode optimizations"""
    
    def __init__(self, 
                 database_url: str,
                 min_connections: int = 5,
                 max_connections: int = 50,
                 max_overflow: int = 10,
                 pool_timeout: int = 30,
                 pool_recycle: int = 3600,
                 pool_pre_ping: bool = True,
                 enable_monitoring: bool = True):
        """Initialize optimized connection pool"""
        
        self.database_url = database_url
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.pool_pre_ping = pool_pre_ping
        self.enable_monitoring = enable_monitoring
        
        self.metrics = PoolMetrics()
        self.lock = threading.Lock()
        self._query_times = []
        self._checkout_times = []
        
        # Create optimized SQLAlchemy engine
        self.engine = self._create_engine()
        self._setup_event_listeners()
        
        logger.info(f"Initialized OptimizedConnectionPool: {min_connections}-{max_connections} connections")
    
    def _create_engine(self) -> sa.Engine:
        """Create optimized SQLAlchemy engine with advanced pooling"""
        
        # Connection pool arguments
        pool_kwargs = {
            'poolclass': QueuePool,
            'pool_size': self.min_connections,
            'max_overflow': self.max_overflow,
            'pool_timeout': self.pool_timeout,
            'pool_recycle': self.pool_recycle,
            'pool_pre_ping': self.pool_pre_ping,
        }
        
        # Engine arguments for optimal performance
        engine_kwargs = {
            'echo': False,
            'connect_args': {
                'connect_timeout': 10,
                'command_timeout': 30,
                'application_name': 'RouteForce_BeastMode'
            },
            'execution_options': {
                'isolation_level': 'READ_COMMITTED',
                'autocommit': False
            }
        }
        
        # Create engine with optimizations
        engine = create_engine(
            self.database_url,
            **pool_kwargs,
            **engine_kwargs
        )
        
        return engine
    
    def _setup_event_listeners(self):
        """Setup SQLAlchemy event listeners for monitoring"""
        
        if not self.enable_monitoring:
            return
        
        @event.listens_for(self.engine, 'connect')
        def on_connect(dbapi_conn, connection_record):
            with self.lock:
                self.metrics.connections_created += 1
                self.metrics.connections_active += 1
        
        @event.listens_for(self.engine, 'checkout')
        def on_checkout(dbapi_conn, connection_record, connection_proxy):
            connection_record._checkout_time = time.time()
            with self.lock:
                self.metrics.connections_checked_out += 1
        
        @event.listens_for(self.engine, 'checkin')
        def on_checkin(dbapi_conn, connection_record):
            if hasattr(connection_record, '_checkout_time'):
                checkout_time = time.time() - connection_record._checkout_time
                with self.lock:
                    self._checkout_times.append(checkout_time)
                    if len(self._checkout_times) > 1000:  # Keep recent 1000 samples
                        self._checkout_times = self._checkout_times[-500:]
                    self.metrics.avg_checkout_time = sum(self._checkout_times) / len(self._checkout_times)
        
        @event.listens_for(self.engine, 'close')
        def on_close(dbapi_conn, connection_record):
            with self.lock:
                self.metrics.connections_closed += 1
                self.metrics.connections_active = max(0, self.metrics.connections_active - 1)
        
        @event.listens_for(self.engine, 'invalidate')
        def on_invalidate(dbapi_conn, connection_record, exception):
            with self.lock:
                self.metrics.connections_invalid += 1
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        
        start_time = time.time()
        connection = None
        
        try:
            connection = self.engine.connect()
            yield connection
            
        except Exception as e:
            with self.lock:
                self.metrics.failed_queries += 1
            logger.error(f"Database connection error: {e}")
            raise
            
        finally:
            if connection:
                connection.close()
            
            # Update metrics
            query_time = time.time() - start_time
            with self.lock:
                self.metrics.total_queries += 1
                self._query_times.append(query_time)
                if len(self._query_times) > 1000:  # Keep recent 1000 samples
                    self._query_times = self._query_times[-500:]
                self.metrics.avg_query_time = sum(self._query_times) / len(self._query_times)
    
    def execute_query(self, query: Union[str, sa.sql.ClauseElement], 
                     parameters: Optional[Dict] = None) -> Any:
        """Execute database query with optimized connection handling"""
        
        with self.get_connection() as conn:
            if isinstance(query, str):
                result = conn.execute(sa.text(query), parameters or {})
            else:
                result = conn.execute(query, parameters or {})
            
            return result.fetchall() if result.returns_rows else result
    
    def execute_transaction(self, operations: List[Callable]) -> bool:
        """Execute multiple operations in a single transaction"""
        
        with self.get_connection() as conn:
            trans = conn.begin()
            try:
                for operation in operations:
                    operation(conn)
                trans.commit()
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"Transaction failed: {e}")
                raise
    
    def batch_execute(self, query: str, parameter_sets: List[Dict]) -> int:
        """Execute batch operations for improved performance"""
        
        if not parameter_sets:
            return 0
        
        with self.get_connection() as conn:
            result = conn.execute(sa.text(query), parameter_sets)
            return result.rowcount if hasattr(result, 'rowcount') else len(parameter_sets)
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get current connection pool status"""
        
        pool = self.engine.pool
        
        return {
            'size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalid': pool.invalid(),
            'metrics': self.metrics,
            'performance_score': self.metrics.performance_score()
        }
    
    def optimize_pool(self) -> Dict[str, Any]:
        """Optimize pool settings based on current metrics"""
        
        status = self.get_pool_status()
        optimization_actions = []
        
        # Check for pool overflow issues
        if status['overflow'] > self.max_overflow * 0.8:
            optimization_actions.append("Consider increasing max_overflow")
        
        # Check for utilization issues
        utilization = self.metrics.utilization_rate()
        if utilization > 0.9:
            optimization_actions.append("Consider increasing pool_size")
        elif utilization < 0.3:
            optimization_actions.append("Consider decreasing pool_size")
        
        # Check for performance issues
        if self.metrics.avg_query_time > 1.0:
            optimization_actions.append("Query performance issues detected")
        
        if self.metrics.avg_checkout_time > 0.1:
            optimization_actions.append("Connection checkout time high")
        
        return {
            'current_status': status,
            'optimization_actions': optimization_actions,
            'performance_score': self.metrics.performance_score()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive pool health check"""
        
        health_status = {
            'status': 'healthy',
            'issues': [],
            'warnings': [],
            'metrics': self.metrics
        }
        
        try:
            # Test basic connectivity
            with self.get_connection() as conn:
                conn.execute(sa.text("SELECT 1"))
            
            # Check pool metrics
            if self.metrics.error_rate() > 0.05:  # 5% error rate threshold
                health_status['issues'].append(f"High error rate: {self.metrics.error_rate():.2%}")
                health_status['status'] = 'unhealthy'
            
            if self.metrics.utilization_rate() > 0.95:
                health_status['warnings'].append("Very high pool utilization")
            
            if self.metrics.avg_query_time > 5.0:
                health_status['issues'].append("Slow query performance detected")
                health_status['status'] = 'degraded'
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['issues'].append(f"Connection test failed: {e}")
        
        return health_status
    
    def reset_metrics(self):
        """Reset performance metrics"""
        with self.lock:
            self.metrics = PoolMetrics()
            self._query_times.clear()
            self._checkout_times.clear()
        
        logger.info("Connection pool metrics reset")
    
    def close(self):
        """Close connection pool"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.info("Connection pool closed")


# Global connection pool instance
_connection_pool: Optional[OptimizedConnectionPool] = None


def initialize_connection_pool(database_url: str, **kwargs) -> OptimizedConnectionPool:
    """Initialize global connection pool"""
    global _connection_pool
    
    if _connection_pool:
        _connection_pool.close()
    
    _connection_pool = OptimizedConnectionPool(database_url, **kwargs)
    return _connection_pool


def get_connection_pool() -> Optional[OptimizedConnectionPool]:
    """Get global connection pool instance"""
    return _connection_pool


def execute_with_pool(query: str, parameters: Optional[Dict] = None) -> Any:
    """Execute query using global connection pool"""
    if not _connection_pool:
        raise RuntimeError("Connection pool not initialized")
    
    return _connection_pool.execute_query(query, parameters)
