import pytest
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Activity
from tests.conftest import get_activity_id

pytestmark = pytest.mark.anyio


async def test_rejects_activity_deeper_than_third_level(
    seeded_session: AsyncSession,
) -> None:
    parent_id = await get_activity_id(
        seeded_session, 'Запчасти для грузовых автомобилей'
    )
    seeded_session.add(
        Activity(
            name='Деятельность',
            parent_id=parent_id,
            level=3,
        )
    )

    with pytest.raises(
        DBAPIError,
        match='Activity hierarchy depth cannot exceed 3 levels.',
    ):
        await seeded_session.commit()

    await seeded_session.rollback()


async def test_rejects_activity_level_mismatch(
    seeded_session: AsyncSession,
) -> None:
    parent_id = await get_activity_id(seeded_session, 'Еда')
    seeded_session.add(
        Activity(
            name='Неверный уровень активности',
            parent_id=parent_id,
            level=3,
        )
    )

    with pytest.raises(
        DBAPIError,
        match='Activity level must match its depth in the hierarchy.',
    ):
        await seeded_session.commit()

    await seeded_session.rollback()
