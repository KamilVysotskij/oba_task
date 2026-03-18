import asyncio
import os
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command
from app.api.dependencies import get_db_session
from app.db.models import Activity, Building, Organization
from app.db.seed import seed_database
from app.main import app
from app.scripts.postgres_db import drop_database, recreate_database

DEFAULT_TEST_DATABASE_URL = (
    'postgresql+psycopg://postgres:postgres@localhost:5432/oba_test'
)


@pytest.fixture(scope='session')
def test_database_url() -> str:
    return os.getenv('TEST_DATABASE_URL', DEFAULT_TEST_DATABASE_URL)


@pytest.fixture(scope='session')
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope='session')
def session_factory(
    test_database_url: str,
) -> Generator[async_sessionmaker[AsyncSession], None, None]:
    test_db_prepared = os.getenv('TEST_DB_PREPARED') == '1'
    if not test_db_prepared:
        recreate_database(test_database_url)
        _run_migrations(test_database_url)

    engine = create_async_engine(test_database_url, pool_pre_ping=True)
    testing_session_local = async_sessionmaker[AsyncSession](
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    asyncio.run(_seed_database(testing_session_local))

    yield testing_session_local

    asyncio.run(engine.dispose())
    drop_database(test_database_url)


@pytest.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://testserver',
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
async def seeded_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


async def get_activity_id(session: AsyncSession, name: str) -> int:
    statement = select(Activity.id).where(Activity.name == name)
    activity_id = await session.scalar(statement)
    assert activity_id is not None
    return activity_id


async def get_organization_id(session: AsyncSession, name: str) -> int:
    statement = select(Organization.id).where(Organization.name == name)
    organization_id = await session.scalar(statement)
    assert organization_id is not None
    return organization_id


async def get_building_id(session: AsyncSession, address: str) -> int:
    statement = select(Building.id).where(Building.address == address)
    building_id = await session.scalar(statement)
    assert building_id is not None
    return building_id


async def _seed_database(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        await seed_database(session, reset=True)


def _run_migrations(database_url: str) -> None:
    alembic_config = Config(
        str(Path(__file__).resolve().parents[1] / 'alembic.ini')
    )
    alembic_config.set_main_option('sqlalchemy.url', database_url)
    command.upgrade(alembic_config, 'head')
