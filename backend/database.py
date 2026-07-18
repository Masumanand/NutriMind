from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis

from config import settings

# ── Database URL normalisation ────────────────────────────────────────────────
# Supports SQLite (local dev) and PostgreSQL (production)
_db_url = settings.DATABASE_URL
if _db_url.startswith("sqlite"):
    # SQLite: use aiosqlite driver
    if not _db_url.startswith("sqlite+aiosqlite"):
        _db_url = _db_url.replace("sqlite://", "sqlite+aiosqlite://")
    engine = create_async_engine(_db_url, echo=False, connect_args={"check_same_thread": False})
else:
    # PostgreSQL: ensure asyncpg driver
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(_db_url, echo=False, pool_size=10, max_overflow=20)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── MongoDB (food logs, social posts) ────────────────────────────────────────
# Falls back gracefully if MongoDB is not running locally
try:
    mongo_client = AsyncIOMotorClient(
        settings.MONGO_URL,
        serverSelectionTimeoutMS=2000,
    )
    mongo_db = mongo_client.nutrimind
except Exception:
    mongo_client = None
    mongo_db = None


def get_mongo():
    return mongo_db


# ── Redis (sessions, cache, streaks) ─────────────────────────────────────────
# Falls back to a simple in-memory mock if Redis is not running locally
class _FakeRedis:
    """Minimal in-memory Redis stub for local dev without Redis."""
    def __init__(self):
        self._store: dict = {}

    async def get(self, key):
        return self._store.get(key)

    async def set(self, key, value, ex=None):
        self._store[key] = value

    async def delete(self, key):
        self._store.pop(key, None)

    async def rpush(self, key, *values):
        self._store.setdefault(key, []).extend(values)

    async def lrange(self, key, start, end):
        lst = self._store.get(key, [])
        return lst[start:end + 1 if end != -1 else None]

    async def ltrim(self, key, start, end):
        lst = self._store.get(key, [])
        self._store[key] = lst[start:end + 1 if end != -1 else None]

    async def expire(self, key, seconds):
        pass

    async def incr(self, key):
        val = int(self._store.get(key, 0)) + 1
        self._store[key] = str(val)
        return val


try:
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
except Exception:
    redis_client = _FakeRedis()


async def get_redis():
    return redis_client
