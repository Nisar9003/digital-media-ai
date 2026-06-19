import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
_pool = None

async def startup_db():
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    print("✅ PostgreSQL connected")

    # Auto-create tables if they don't exist
    async with _pool.acquire() as conn:
        await conn.execute("""
            CREATE EXTENSION IF NOT EXISTS "pgcrypto";

            CREATE TABLE IF NOT EXISTS campaigns (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                goal        TEXT NOT NULL,
                brief       TEXT,
                status      VARCHAR(20) DEFAULT 'active',
                created_at  TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS posts (
                id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                campaign_id  UUID REFERENCES campaigns(id) ON DELETE CASCADE,
                platform     VARCHAR(50),
                content      TEXT,
                image_url    TEXT,
                status       VARCHAR(20) DEFAULT 'draft',
                feedback     TEXT,
                published_at TIMESTAMPTZ,
                created_at   TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS agent_logs (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                run_id      VARCHAR(100),
                post_id     UUID REFERENCES posts(id) ON DELETE CASCADE,
                agent_name  VARCHAR(50),
                input       TEXT,
                output      TEXT,
                tokens_used INTEGER,
                duration_ms INTEGER,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS analytics (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                post_id     UUID REFERENCES posts(id) ON DELETE CASCADE,
                platform    VARCHAR(50),
                likes       INTEGER DEFAULT 0,
                comments    INTEGER DEFAULT 0,
                shares      INTEGER DEFAULT 0,
                clicks      INTEGER DEFAULT 0,
                reach       INTEGER DEFAULT 0,
                recorded_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS image_iterations (
                id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                post_id    UUID REFERENCES posts(id) ON DELETE CASCADE,
                iteration  INTEGER DEFAULT 1,
                prompt     TEXT,
                image_url  TEXT,
                feedback   TEXT,
                status     VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        print("✅ All tables ready")

async def shutdown_db():
    global _pool
    if _pool:
        await _pool.close()
        print("PostgreSQL disconnected")

def get_pool():
    return _pool