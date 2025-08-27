"""
Mobile App Service Layer for RouteForce Routing
React Native service layer with offline capabilities and real-time sync
"""

import json
import sqlite3
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from enum import Enum


class SyncStatus(Enum):
    PENDING = "pending"
    SYNCING = "syncing" 
    SYNCED = "synced"
    FAILED = "failed"
    OFFLINE = "offline"


class ConnectionStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    LIMITED = "limited"


@dataclass
class RouteData:
    """Route data structure for mobile app"""
    id: str
    name: str
    stops: List[Dict[str, Any]]
    driver_id: str
    status: str
    created_at: str
    updated_at: str
    sync_status: str = SyncStatus.PENDING.value
    local_changes: bool = False


@dataclass
class DriverLocation:
    """Driver location data"""
    driver_id: str
    latitude: float
    longitude: float
    timestamp: str
    accuracy: float
    speed: Optional[float] = None
    heading: Optional[float] = None


class OfflineStorage:
    """SQLite-based offline storage for mobile app"""
    
    def __init__(self, db_path: str = "routeforce_mobile.db"):
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Create tables
        cursor = self.connection.cursor()
        
        # Routes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                stops TEXT NOT NULL,
                driver_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                sync_status TEXT DEFAULT 'pending',
                local_changes INTEGER DEFAULT 0
            )
        """)
        
        # Driver locations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS driver_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timestamp TEXT NOT NULL,
                accuracy REAL NOT NULL,
                speed REAL,
                heading REAL,
                sync_status TEXT DEFAULT 'pending'
            )
        """)
        
        # Route progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS route_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id TEXT NOT NULL,
                stop_id TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                notes TEXT,
                photo_path TEXT,
                sync_status TEXT DEFAULT 'pending'
            )
        """)
        
        # Sync queue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                retry_count INTEGER DEFAULT 0,
                last_error TEXT
            )
        """)
        
        self.connection.commit()
    
    def store_route(self, route: RouteData) -> bool:
        """Store route data locally"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO routes 
                (id, name, stops, driver_id, status, created_at, updated_at, sync_status, local_changes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                route.id, route.name, json.dumps(route.stops), route.driver_id,
                route.status, route.created_at, route.updated_at, 
                route.sync_status, 1 if route.local_changes else 0
            ))
            self.connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error storing route: {e}")
            return False
    
    def get_route(self, route_id: str) -> Optional[RouteData]:
        """Retrieve route data by ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM routes WHERE id = ?", (route_id,))
            row = cursor.fetchone()
            
            if row:
                return RouteData(
                    id=row['id'],
                    name=row['name'],
                    stops=json.loads(row['stops']),
                    driver_id=row['driver_id'],
                    status=row['status'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    sync_status=row['sync_status'],
                    local_changes=bool(row['local_changes'])
                )
            return None
        except Exception as e:
            logging.error(f"Error retrieving route: {e}")
            return None
    
    def get_pending_sync_data(self) -> List[Dict[str, Any]]:
        """Get all data pending synchronization"""
        try:
            pending_data = []
            cursor = self.connection.cursor()
            
            # Get routes with local changes
            cursor.execute("SELECT * FROM routes WHERE local_changes = 1 OR sync_status = 'pending'")
            routes = cursor.fetchall()
            for route in routes:
                pending_data.append({
                    'type': 'route',
                    'action': 'update',
                    'data': dict(route)
                })
            
            # Get pending location updates
            cursor.execute("SELECT * FROM driver_locations WHERE sync_status = 'pending'")
            locations = cursor.fetchall()
            for location in locations:
                pending_data.append({
                    'type': 'location',
                    'action': 'create',
                    'data': dict(location)
                })
            
            # Get pending route progress
            cursor.execute("SELECT * FROM route_progress WHERE sync_status = 'pending'")
            progress = cursor.fetchall()
            for prog in progress:
                pending_data.append({
                    'type': 'progress',
                    'action': 'create',
                    'data': dict(prog)
                })
            
            return pending_data
        except Exception as e:
            logging.error(f"Error getting pending sync data: {e}")
            return []


class MobileAPIClient:
    """HTTP client for communicating with RouteForce API"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'RouteForce-Mobile/1.0'
            }
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
            )
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_routes(self, driver_id: str) -> List[Dict[str, Any]]:
        """Fetch routes for a driver"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/api/routes/driver/{driver_id}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('routes', [])
                else:
                    logging.error(f"Failed to fetch routes: {response.status}")
                    return []
        except Exception as e:
            logging.error(f"Error fetching routes: {e}")
            return []
    
    async def update_driver_location(self, location: DriverLocation) -> bool:
        """Send driver location update"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/api/drivers/location"
            
            async with session.post(url, json=asdict(location)) as response:
                return response.status in [200, 201]
        except Exception as e:
            logging.error(f"Error updating location: {e}")
            return False
    
    async def update_route_progress(self, route_id: str, stop_id: str, 
                                   status: str, notes: str = None) -> bool:
        """Update route progress"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}/api/routes/{route_id}/progress"
            
            data = {
                'stop_id': stop_id,
                'status': status,
                'timestamp': datetime.utcnow().isoformat(),
                'notes': notes
            }
            
            async with session.post(url, json=data) as response:
                return response.status in [200, 201]
        except Exception as e:
            logging.error(f"Error updating route progress: {e}")
            return False


class MobileService:
    """Main mobile service orchestrating offline storage and sync"""
    
    def __init__(self, api_base_url: str, api_key: str, db_path: str = None):
        self.api_client = MobileAPIClient(api_base_url, api_key)
        self.storage = OfflineStorage(db_path)
        self.connection_status = ConnectionStatus.OFFLINE
        self.sync_interval = 30  # seconds
        self.location_interval = 10  # seconds
        self.is_running = False
        self._sync_task = None
        self._location_task = None
    
    async def start(self):
        """Start the mobile service"""
        self.is_running = True
        
        # Start background tasks
        self._sync_task = asyncio.create_task(self._sync_loop())
        self._location_task = asyncio.create_task(self._location_loop())
        
        logging.info("Mobile service started")
    
    async def stop(self):
        """Stop the mobile service"""
        self.is_running = False
        
        if self._sync_task:
            self._sync_task.cancel()
        if self._location_task:
            self._location_task.cancel()
        
        await self.api_client.close()
        logging.info("Mobile service stopped")
    
    async def _sync_loop(self):
        """Background sync loop"""
        while self.is_running:
            try:
                await self.sync_data()
                await asyncio.sleep(self.sync_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Sync loop error: {e}")
                await asyncio.sleep(self.sync_interval)
    
    async def _location_loop(self):
        """Background location update loop"""
        while self.is_running:
            try:
                # This would be implemented with actual GPS in mobile app
                # For now, skip if no location provider
                await asyncio.sleep(self.location_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Location loop error: {e}")
                await asyncio.sleep(self.location_interval)
    
    async def sync_data(self) -> bool:
        """Sync pending data with server"""
        try:
            # Check network connectivity
            session = await self.api_client._get_session()
            async with session.get(f"{self.api_client.base_url}/api/health") as response:
                if response.status != 200:
                    self.connection_status = ConnectionStatus.OFFLINE
                    return False
            
            self.connection_status = ConnectionStatus.ONLINE
            
            # Get pending data
            pending_data = self.storage.get_pending_sync_data()
            
            if not pending_data:
                return True
            
            # Sync each item
            success_count = 0
            for item in pending_data:
                try:
                    if item['type'] == 'location':
                        location = DriverLocation(**item['data'])
                        success = await self.api_client.update_driver_location(location)
                    elif item['type'] == 'progress':
                        data = item['data']
                        success = await self.api_client.update_route_progress(
                            data['route_id'], data['stop_id'], 
                            data['status'], data.get('notes')
                        )
                    else:
                        success = True  # Handle other types
                    
                    if success:
                        success_count += 1
                        # Mark as synced in local storage
                        # Implementation would update sync_status
                
                except Exception as e:
                    logging.error(f"Error syncing item {item}: {e}")
            
            logging.info(f"Synced {success_count}/{len(pending_data)} items")
            return success_count == len(pending_data)
            
        except Exception as e:
            logging.error(f"Sync error: {e}")
            self.connection_status = ConnectionStatus.OFFLINE
            return False
    
    async def get_driver_routes(self, driver_id: str, force_sync: bool = False) -> List[RouteData]:
        """Get routes for a driver (local first, sync if needed)"""
        routes = []
        
        if force_sync or self.connection_status == ConnectionStatus.ONLINE:
            try:
                # Fetch from server
                server_routes = await self.api_client.get_routes(driver_id)
                
                for route_data in server_routes:
                    route = RouteData(
                        id=route_data['id'],
                        name=route_data['name'],
                        stops=route_data['stops'],
                        driver_id=route_data['driver_id'],
                        status=route_data['status'],
                        created_at=route_data['created_at'],
                        updated_at=route_data['updated_at'],
                        sync_status=SyncStatus.SYNCED.value
                    )
                    
                    # Store locally
                    self.storage.store_route(route)
                    routes.append(route)
            
            except Exception as e:
                logging.error(f"Error fetching routes from server: {e}")
        
        # If no routes from server or offline, get from local storage
        if not routes:
            # Implementation would query local database for driver routes
            pass
        
        return routes
    
    async def update_route_progress(self, route_id: str, stop_id: str, 
                                   status: str, notes: str = None) -> bool:
        """Update route progress (local first, sync later)"""
        try:
            # Store locally first
            cursor = self.storage.connection.cursor()
            cursor.execute("""
                INSERT INTO route_progress 
                (route_id, stop_id, status, timestamp, notes, sync_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                route_id, stop_id, status, 
                datetime.utcnow().isoformat(), notes, 
                SyncStatus.PENDING.value
            ))
            self.storage.connection.commit()
            
            # Try immediate sync if online
            if self.connection_status == ConnectionStatus.ONLINE:
                await self.api_client.update_route_progress(route_id, stop_id, status, notes)
            
            return True
            
        except Exception as e:
            logging.error(f"Error updating route progress: {e}")
            return False


# Configuration for mobile app
MOBILE_CONFIG = {
    'sync_interval': 30,
    'location_interval': 10,
    'offline_retention_days': 30,
    'max_retry_attempts': 3,
    'batch_sync_size': 50,
    'compression_enabled': True,
    'encryption_enabled': True
}


# Export main classes
__all__ = [
    'MobileService',
    'OfflineStorage', 
    'MobileAPIClient',
    'RouteData',
    'DriverLocation',
    'SyncStatus',
    'ConnectionStatus',
    'MOBILE_CONFIG'
]
