from __future__ import annotations

import re

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError


def recreate_database(database_url: str | URL) -> None:
    url = _as_url(database_url)
    _validate_database_name(url.database)

    admin_engine = create_engine(
        url.set(database='postgres'),
        isolation_level='AUTOCOMMIT',
        pool_pre_ping=True,
    )

    try:
        with admin_engine.connect() as connection:
            try:
                connection.execute(text('SELECT 1'))
            except OperationalError as exc:
                raise RuntimeError(
                    'PostgreSQL is not available. Start it first, for example with `docker compose up -d db`.'
                ) from exc

            _terminate_connections(connection, url.database)
            connection.execute(
                text(f'DROP DATABASE IF EXISTS "{url.database}"')
            )
            connection.execute(text(f'CREATE DATABASE "{url.database}"'))
    finally:
        admin_engine.dispose()


def ensure_database(database_url: str | URL) -> None:
    url = _as_url(database_url)
    _validate_database_name(url.database)

    admin_engine = create_engine(
        url.set(database='postgres'),
        isolation_level='AUTOCOMMIT',
        pool_pre_ping=True,
    )

    try:
        with admin_engine.connect() as connection:
            try:
                connection.execute(text('SELECT 1'))
            except OperationalError as exc:
                raise RuntimeError(
                    'PostgreSQL is not available. Start it first, for example with `docker compose up -d db`.'
                ) from exc

            exists = connection.execute(
                text(
                    'SELECT 1 FROM pg_database WHERE datname = :database_name'
                ),
                {'database_name': url.database},
            ).scalar()
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{url.database}"'))
    finally:
        admin_engine.dispose()


def drop_database(database_url: str | URL) -> None:
    url = _as_url(database_url)
    _validate_database_name(url.database)

    admin_engine = create_engine(
        url.set(database='postgres'),
        isolation_level='AUTOCOMMIT',
        pool_pre_ping=True,
    )

    try:
        with admin_engine.connect() as connection:
            _terminate_connections(connection, url.database)
            connection.execute(
                text(f'DROP DATABASE IF EXISTS "{url.database}"')
            )
    finally:
        admin_engine.dispose()


def _terminate_connections(connection, database_name: str) -> None:
    connection.execute(
        text(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = :database_name
              AND pid <> pg_backend_pid()
            """
        ),
        {'database_name': database_name},
    )


def _as_url(database_url: str | URL) -> URL:
    return (
        make_url(database_url)
        if isinstance(database_url, str)
        else database_url
    )


def _validate_database_name(database_name: str | None) -> None:
    if (
        database_name is None
        or re.fullmatch(r'[A-Za-z0-9_]+', database_name) is None
    ):
        raise ValueError(
            'Database name must contain only letters, numbers, and underscores.'
        )
