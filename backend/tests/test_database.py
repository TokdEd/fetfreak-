import pytest
from ..database import DatabaseConnection
import os

@pytest.mark.asyncio
async def test_database_connection():
    db = DatabaseConnection()
    await db.connect()
    assert db._pool is not None
    await db.close()
    assert db._pool is None

@pytest.mark.asyncio
async def test_execute_query():
    db = DatabaseConnection()
    await db.connect()
    
    # 測試執行查詢
    query = """
        SELECT User {
            name,
            email
        }
        FILTER .email = <str>$email
    """
    result = await db.execute_single(query, email="test@example.com")
    assert result is None or isinstance(result, dict)
    
    await db.close()

@pytest.mark.asyncio
async def test_connection_pool():
    db = DatabaseConnection()
    await db.connect()
    
    # 測試連接池並發
    async def test_query():
        async with db.get_connection() as conn:
            return await conn.query_single("SELECT 1")
    
    # 同時執行多個查詢
    import asyncio
    tasks = [test_query() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    assert all(r == 1 for r in results)
    await db.close() 