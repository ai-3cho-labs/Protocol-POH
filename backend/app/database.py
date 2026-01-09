"""
$COPPER Database Connection

Async PostgreSQL connection using SQLAlchemy with asyncpg.
"""

import ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from app.config import get_settings

settings = get_settings()


def prepare_database_url(url: str) -> tuple[str, dict]:
    """
    Prepare database URL for the appropriate async driver.

    For PostgreSQL: Converts postgres:// to postgresql+asyncpg:// and handles SSL.
    For SQLite: Returns URL as-is with empty connect_args.
    """
    # Handle SQLite URLs - return as-is (no special processing needed)
    if url.startswith("sqlite"):
        return url, {}

    # Convert PostgreSQL to asyncpg driver
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Parse URL and remove sslmode from query params (asyncpg doesn't support it)
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)

    # Check if SSL is required
    ssl_mode = query_params.pop("sslmode", ["require"])[0]
    needs_ssl = ssl_mode in ("require", "verify-ca", "verify-full")

    # Rebuild URL without sslmode
    new_query = urlencode(query_params, doseq=True)
    clean_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

    # Build connect_args with proper SSL context for asyncpg
    connect_args = {
        "command_timeout": 30,  # 30 second query timeout
    }

    if needs_ssl:
        # Create SSL context for asyncpg with proper certificate verification
        ssl_context = ssl.create_default_context()
        # SECURITY: Enable certificate verification to prevent MITM attacks
        # Neon PostgreSQL uses valid certificates that should be verified
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        connect_args["ssl"] = ssl_context

    return clean_url, connect_args


# Prepare database URL and connection args
database_url, connect_args = prepare_database_url(settings.database_url)

# Check if using SQLite
is_sqlite = database_url.startswith("sqlite")

# Create async engine
# Use NullPool for serverless (Neon) - pool_size/max_overflow not compatible with NullPool
engine_kwargs = {
    "echo": settings.debug,
}

if is_sqlite:
    # SQLite-specific configuration
    from sqlalchemy.pool import StaticPool
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = StaticPool
elif settings.is_production:
    # NullPool for serverless PostgreSQL - no connection pooling
    engine_kwargs["connect_args"] = connect_args
    engine_kwargs["poolclass"] = NullPool
else:
    # Connection pooling for local PostgreSQL development
    engine_kwargs["connect_args"] = connect_args
    engine_kwargs["poolclass"] = AsyncAdaptedQueuePool
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10
    engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(database_url, **engine_kwargs)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency that provides a database session.

    Usage:
        @app.get("/")
        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database connection (for startup)."""
    async with engine.begin() as conn:
        # Verify connection works using proper text() wrapper
        await conn.execute(text("SELECT 1"))


async def close_db():
    """Close database connections (for shutdown)."""
    await engine.dispose()
