import argparse
import logging
import os

from app.scripts.postgres_db import drop_database

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(description='Drop a PostgreSQL database.')
    parser.add_argument(
        '--database-url',
        default=os.getenv('DATABASE_URL'),
        help='Database URL to drop. Defaults to DATABASE_URL.',
    )
    args = parser.parse_args()

    if not args.database_url:
        raise ValueError('DATABASE_URL is required.')

    drop_database(args.database_url)
    logger.info('Database dropped.')
