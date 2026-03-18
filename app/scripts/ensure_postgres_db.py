import argparse
import logging
import os

from app.scripts.postgres_db import ensure_database

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(
        description='Ensure a PostgreSQL database exists.'
    )
    parser.add_argument(
        '--database-url',
        default=os.getenv('DATABASE_URL'),
        help='Database URL to ensure. Defaults to DATABASE_URL.',
    )
    args = parser.parse_args()

    if not args.database_url:
        raise ValueError('DATABASE_URL is required.')

    ensure_database(args.database_url)
    logger.info('Database ensured.')
