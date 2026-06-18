import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
_pool = None

async def startup_db():
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    print("PostgreSQL connected")

async def shutdown_db():
    global _pool
    if _pool:
        await _pool.close()
        print("PostgreSQL disconnected")

def get_pool():
    return _pool
