# database.py
import os
import edgedb
from dotenv import load_dotenv
from typing import Optional
from contextlib import asynccontextmanager
import pathlib

# 打印當前工作目錄和.env文件位置
print(f"Current working directory: {pathlib.Path.cwd()}")
print(f"Looking for .env file in: {pathlib.Path.cwd() / '.env'}")
print(f".env file exists: {(pathlib.Path.cwd() / '.env').exists()}")

# 加載環境變量
load_dotenv()

print(f"Instance: {os.getenv('EDGEDB_INSTANCE')}")
print(f"Secret key exists: {bool(os.getenv('EDGEDB_SECRET_KEY'))}")

class DatabaseConnection:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def get_client(self):
        """
        獲取數據庫客戶端實例
        """
        return self._pool

    async def connect(self):
        try:
            # 獲取環境變量
            instance = os.getenv('EDGEDB_INSTANCE')
            secret_key = os.getenv('EDGEDB_SECRET_KEY')

            if not instance or not secret_key:
                raise ValueError("EdgeDB credentials not found in environment variables")

            self._pool = edgedb.create_async_client(
                dsn=f"edgedb://{instance}?secret_key={secret_key}"
            )
            # 測試連接
            await self._pool.query('SELECT 1')
            print("Database connected successfully")
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            if "credentials not found" in str(e):
                print("Please check your EDGEDB_INSTANCE and EDGEDB_SECRET_KEY environment variables")
            raise

    async def close(self):
        if self._pool:
            await self._pool.aclose()
            self._pool = None

    @asynccontextmanager
    async def get_connection(self):
        if not self._pool:
            await self.connect()
        async with self._pool.acquire() as conn:
            yield conn

    async def execute(self, query: str, **kwargs):
        async with self.get_connection() as conn:
            try:
                return await conn.query(query, **kwargs)
            except Exception as e:
                print(f"Query execution error: {e}")
                raise

    async def execute_single(self, query: str, **kwargs):
        async with self.get_connection() as conn:
            try:
                return await conn.query_single(query, **kwargs)
            except Exception as e:
                print(f"Query execution error: {e}")
                raise

class Database:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    async def create_user(self, name: str, email: str, password: str):
        """
        創建新用戶
        """
        if not self.db_connection.get_client():
            await self.db_connection.connect()
        query = """
            INSERT User {
                name := <str>$name,
                email := <str>$email,
                password := <str>$password
            }
        """
        try:
            return await self.db_connection.execute_single(query, name=name, email=email, password=password)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    async def get_user_by_email(self, email: str):
        """
        通過郵箱查詢用戶
        """
        if not self.db_connection.get_client():
            await self.db_connection.connect()
        query = """
            SELECT User {
                name,
                email
            }
            FILTER .email = <str>$email
        """
        try:
            return await self.db_connection.execute_single(query, email=email)
        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    async def get_all_users(self):
        """
        獲取所有用戶
        """
        if not self.db_connection.get_client():
            await self.db_connection.connect()
        query = """
            SELECT User {
                name,
                email
            }
        """
        try:
            return await self.db_connection.execute(query)
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    async def update_user(self, email: str, new_name: str = None, new_email: str = None):
        """
        更新用戶信息
        """
        if not self.db_connection.get_client():
            await self.db_connection.connect()
        updates = []
        if new_name:
            updates.append(f"name := <str>$new_name")
        if new_email:
            updates.append(f"email := <str>$new_email")
        
        if not updates:
            return None

        query = f"""
            UPDATE User 
            FILTER .email = <str>$email
            SET {{
                {', '.join(updates)}
            }}
        """
        try:
            return await self.db_connection.execute_single(
                query,
                email=email,
                new_name=new_name,
                new_email=new_email
            )
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    async def delete_user(self, email: str):
        """
        刪除用戶
        """
        if not self.db_connection.get_client():
            await self.db_connection.connect()
        query = """
            DELETE User 
            FILTER .email = <str>$email
        """
        try:
            return await self.db_connection.execute_single(query, email=email)
        except Exception as e:
            print(f"Error deleting user: {e}")
            return None

# 使用示例
"""
async def main():
    db = Database()
    
    # 創建用戶
    await db.create_user("John Doe", "john@example.com", "password123")
    
    # 查詢用戶
    user = await db.get_user_by_email("john@example.com")
    print(user)
    
    # 更新用戶
    await db.update_user("john@example.com", new_name="John Smith")
    
    # 獲取所有用戶
    all_users = await db.get_all_users()
    print(all_users)
    
    # 刪除用戶
    await db.delete_user("john@example.com")

# 運行
import asyncio
asyncio.run(main())
"""