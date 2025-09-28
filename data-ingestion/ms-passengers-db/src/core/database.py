"""
Database Manager for MS-Passengers PostgreSQL Connection
Handles connection pooling, CDC setup, and database operations
"""

import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime, timezone
import json
from contextlib import asynccontextmanager

import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from config.settings import Settings, DatabaseSettings
from utils.logger import get_logger, log_database_operation


class DatabaseManager:
    """PostgreSQL database manager with CDC support"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.db_settings = settings.database
        self.logger = get_logger(self.__class__.__name__)
        
        # Connection pools
        self._async_engine = None
        self._sync_engine = None
        self._connection_pool = None
        self._async_session_factory = None
        
        # CDC components
        self._replication_connection = None
        self._replication_slot = None
        
        # Metadata
        self._metadata = MetaData()
        self._tables: Dict[str, Table] = {}
        
    async def initialize(self):
        """Initialize database connections and CDC"""
        self.logger.info("Initializing database manager")
        
        try:
            # Create async engine
            self._async_engine = create_async_engine(
                self.db_settings.async_connection_url,
                pool_size=self.db_settings.pool_size,
                max_overflow=self.db_settings.max_overflow,
                pool_timeout=self.db_settings.pool_timeout,
                pool_recycle=self.db_settings.pool_recycle,
                echo=self.settings.debug
            )
            
            # Create sync engine for CDC
            self._sync_engine = create_engine(
                self.db_settings.connection_url,
                poolclass=NullPool,
                echo=self.settings.debug
            )
            
            # Create session factory
            self._async_session_factory = sessionmaker(
                self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create connection pool
            self._connection_pool = await asyncpg.create_pool(
                host=self.db_settings.host,
                port=self.db_settings.port,
                database=self.db_settings.database,
                user=self.db_settings.user,
                password=self.db_settings.password,
                min_size=2,
                max_size=self.db_settings.pool_size,
                command_timeout=60
            )
            
            # Load table metadata
            await self._load_metadata()
            
            # Setup CDC if enabled
            if self.settings.ingestion.cdc_enabled:
                await self._setup_cdc()
            
            self.logger.info("Database manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database manager: {str(e)}", exc_info=True)
            raise
    
    async def close(self):
        """Close all database connections"""
        self.logger.info("Closing database connections")
        
        try:
            if self._connection_pool:
                await self._connection_pool.close()
            
            if self._async_engine:
                await self._async_engine.dispose()
            
            if self._sync_engine:
                self._sync_engine.dispose()
            
            if self._replication_connection:
                self._replication_connection.close()
                
        except Exception as e:
            self.logger.error(f"Error closing database connections: {str(e)}")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool"""
        async with self._connection_pool.acquire() as connection:
            yield connection
    
    @asynccontextmanager
    async def get_session(self):
        """Get an async SQLAlchemy session"""
        async with self._async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            start_time = datetime.now()
            
            async with self.get_connection() as conn:
                # Test basic connectivity
                result = await conn.fetchval("SELECT 1")
                
                # Get database stats
                stats = await conn.fetchrow("""
                    SELECT 
                        pg_database_size(current_database()) as db_size,
                        (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
                        (SELECT count(*) FROM passengers) as passenger_count
                """)
                
                # Check replication status if CDC enabled
                replication_status = None
                if self.settings.ingestion.cdc_enabled:
                    replication_status = await self._check_replication_status(conn)
                
                duration = (datetime.now() - start_time).total_seconds()
                
                return {
                    "status": "healthy",
                    "connection_test": result == 1,
                    "response_time_ms": int(duration * 1000),
                    "database_size_bytes": stats["db_size"],
                    "active_connections": stats["active_connections"],
                    "passenger_count": stats["passenger_count"],
                    "replication_status": replication_status
                }
                
        except Exception as e:
            self.logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _load_metadata(self):
        """Load table metadata from database"""
        try:
            async with self._async_engine.begin() as conn:
                # Reflect passengers table
                await conn.run_sync(self._metadata.reflect)
                
                # Store table references
                if 'passengers' in self._metadata.tables:
                    self._tables['passengers'] = self._metadata.tables['passengers']
                    self.logger.info("Loaded passengers table metadata")
                else:
                    self.logger.warning("Passengers table not found in database")
                    
        except Exception as e:
            self.logger.error(f"Failed to load table metadata: {str(e)}")
            raise
    
    async def _setup_cdc(self):
        """Setup Change Data Capture for PostgreSQL"""
        try:
            self.logger.info("Setting up PostgreSQL CDC")
            
            # Create replication connection
            self._replication_connection = psycopg2.connect(
                host=self.db_settings.host,
                port=self.db_settings.port,
                database=self.db_settings.database,
                user=self.db_settings.user,
                password=self.db_settings.password,
                connection_factory=psycopg2.extras.LogicalReplicationConnection
            )
            
            # Create replication slot if it doesn't exist
            cursor = self._replication_connection.cursor()
            
            try:
                cursor.execute(
                    "SELECT slot_name FROM pg_replication_slots WHERE slot_name = %s",
                    (self.settings.ingestion.cdc_slot_name,)
                )
                
                if not cursor.fetchone():
                    cursor.execute(
                        "SELECT pg_create_logical_replication_slot(%s, 'pgoutput')",
                        (self.settings.ingestion.cdc_slot_name,)
                    )
                    self.logger.info(f"Created replication slot: {self.settings.ingestion.cdc_slot_name}")
                else:
                    self.logger.info(f"Replication slot exists: {self.settings.ingestion.cdc_slot_name}")
                
                # Create publication for passengers table
                cursor.execute(f"""
                    CREATE PUBLICATION IF NOT EXISTS {self.settings.ingestion.cdc_publication_name}
                    FOR TABLE passengers
                """)
                self.logger.info(f"Created publication: {self.settings.ingestion.cdc_publication_name}")
                
                self._replication_connection.commit()
                
            except Exception as e:
                self._replication_connection.rollback()
                raise e
            finally:
                cursor.close()
                
        except Exception as e:
            self.logger.error(f"Failed to setup CDC: {str(e)}")
            raise
    
    async def _check_replication_status(self, conn) -> Dict[str, Any]:
        """Check replication slot status"""
        try:
            status = await conn.fetchrow("""
                SELECT 
                    slot_name,
                    plugin,
                    slot_type,
                    database,
                    active,
                    restart_lsn,
                    confirmed_flush_lsn
                FROM pg_replication_slots 
                WHERE slot_name = $1
            """, self.settings.ingestion.cdc_slot_name)
            
            if status:
                return dict(status)
            else:
                return {"error": "Replication slot not found"}
                
        except Exception as e:
            return {"error": str(e)}
    
    async def get_passenger_data(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Extract passenger data with optional filtering"""
        start_time = datetime.now()
        
        try:
            query = "SELECT * FROM passengers"
            params = []
            
            # Add timestamp filter if provided
            if since:
                query += " WHERE updated_at > $1"
                params.append(since)
            
            # Add ordering and pagination
            query += " ORDER BY updated_at, passenger_id"
            
            if limit:
                if since:
                    query += " LIMIT $2 OFFSET $3"
                    params.extend([limit, offset])
                else:
                    query += " LIMIT $1 OFFSET $2"
                    params.extend([limit, offset])
            elif offset > 0:
                if since:
                    query += " OFFSET $2"
                    params.append(offset)
                else:
                    query += " OFFSET $1"
                    params.append(offset)
            
            async with self.get_connection() as conn:
                rows = await conn.fetch(query, *params)
                
                # Convert to dict format
                results = [dict(row) for row in rows]
                
                # Log operation
                duration = (datetime.now() - start_time).total_seconds()
                log_database_operation(
                    self.logger,
                    operation="extract_passengers",
                    query_type="SELECT",
                    duration=duration,
                    rows_affected=len(results),
                    limit=limit,
                    offset=offset,
                    since=since.isoformat() if since else None
                )
                
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to extract passenger data: {str(e)}", exc_info=True)
            raise
    
    async def get_table_count(self, table_name: str = "passengers") -> int:
        """Get total count of records in table"""
        try:
            async with self.get_connection() as conn:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                return count
                
        except Exception as e:
            self.logger.error(f"Failed to get table count: {str(e)}")
            raise
    
    async def get_latest_timestamp(self, table_name: str = "passengers") -> Optional[datetime]:
        """Get the latest updated_at timestamp from table"""
        try:
            async with self.get_connection() as conn:
                timestamp = await conn.fetchval(
                    f"SELECT MAX(updated_at) FROM {table_name}"
                )
                return timestamp
                
        except Exception as e:
            self.logger.error(f"Failed to get latest timestamp: {str(e)}")
            return None
    
    def get_cdc_changes(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Get CDC changes from replication slot"""
        if not self.settings.ingestion.cdc_enabled or not self._replication_connection:
            raise RuntimeError("CDC not enabled or not initialized")
        
        return self._consume_cdc_changes()
    
    async def _consume_cdc_changes(self):
        """Consume changes from logical replication slot"""
        try:
            cursor = self._replication_connection.cursor()
            
            cursor.start_replication(
                slot_name=self.settings.ingestion.cdc_slot_name,
                decode=True,
                status_interval=10
            )
            
            self.logger.info("Started CDC change stream consumption")
            
            for msg in cursor:
                if msg.data_start:
                    try:
                        # Parse logical decoding output
                        change_data = self._parse_cdc_message(msg.payload)
                        if change_data:
                            yield change_data
                    except Exception as e:
                        self.logger.error(f"Error parsing CDC message: {str(e)}")
                        continue
                
                # Send status update
                msg.cursor.send_feedback(flush_lsn=msg.data_start)
                
        except Exception as e:
            self.logger.error(f"CDC consumption error: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def _parse_cdc_message(self, payload: str) -> Optional[Dict[str, Any]]:
        """Parse CDC message payload"""
        try:
            # This is a simplified parser - in production, you'd want a more robust parser
            # for PostgreSQL logical decoding output format
            if "BEGIN" in payload or "COMMIT" in payload:
                return None
            
            # Extract table name and operation
            if "passengers" in payload:
                if "INSERT" in payload:
                    operation = "INSERT"
                elif "UPDATE" in payload:
                    operation = "UPDATE"
                elif "DELETE" in payload:
                    operation = "DELETE"
                else:
                    return None
                
                return {
                    "table": "passengers",
                    "operation": operation,
                    "payload": payload,
                    "timestamp": datetime.now(timezone.utc)
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to parse CDC message: {str(e)}")
            return None
