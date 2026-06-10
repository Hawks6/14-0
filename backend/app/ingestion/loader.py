import logging
from typing import List, Tuple, Any
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

async def bulk_copy_records(db_engine: AsyncEngine, table_name: str, columns: List[str], records: List[Tuple[Any, ...]]):
    """
    Acquires raw asyncpg connection from SQLAlchemy async engine and
    invokes copy_records_to_table to stream records directly to PostgreSQL
    within a transaction.
    """
    if not records:
        logger.info(f"No records provided for bulk copy to {table_name}.")
        return

    async with db_engine.begin() as conn:
        raw_conn = await conn.get_raw_connection()
        driver_conn = raw_conn.driver_connection
        
        await driver_conn.copy_records_to_table(
            table_name,
            records=records,
            columns=columns
        )
        
    logger.info(f"Successfully loaded {len(records)} records into {table_name}")
