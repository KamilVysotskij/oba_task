import asyncio
import argparse
import logging

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def _wait_for_db(attempts: int, delay: float) -> None:
    engine = create_async_engine(
        get_settings().database_url,
        pool_pre_ping=True,
    )
    try:
        for attempt in range(1, attempts + 1):
            try:
                async with engine.connect() as connection:
                    await connection.execute(text('SELECT 1'))
                logger.info('Database is ready.')
                return
            except OperationalError:
                if attempt == attempts:
                    raise
                logger.info(
                    'Database is not ready yet. Attempt %s/%s.',
                    attempt,
                    attempts,
                )
                await asyncio.sleep(delay)
    finally:
        await engine.dispose()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(
        description='Wait until the database is ready.'
    )
    parser.add_argument('--attempts', type=int, default=20)
    parser.add_argument('--delay', type=float, default=2.0)
    args = parser.parse_args()

    asyncio.run(_wait_for_db(args.attempts, args.delay))
