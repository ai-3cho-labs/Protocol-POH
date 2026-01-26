"""Run SQL migrations against the database."""
import asyncio
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

load_dotenv()

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


async def run_migrations():
    """Run all SQL migrations in order."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return

    print(f"Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        # Get all migration files sorted
        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

        for migration_file in migration_files:
            print(f"Running {migration_file.name}...")
            sql = migration_file.read_text()

            try:
                await conn.execute(sql)
                print(f"  [OK] {migration_file.name} completed")
            except asyncpg.exceptions.DuplicateTableError as e:
                print(f"  [SKIP] {migration_file.name} (tables already exist)")
            except asyncpg.exceptions.DuplicateObjectError as e:
                print(f"  [SKIP] {migration_file.name} (objects already exist)")
            except Exception as e:
                print(f"  [FAIL] {migration_file.name}: {e}")

        print("\nMigrations complete!")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())
