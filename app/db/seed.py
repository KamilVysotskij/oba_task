import argparse
import asyncio
import logging

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Activity,
    Building,
    Organization,
    OrganizationPhone,
    organization_activities,
)
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

ACTIVITY_TREE = [
    {
        'name': 'Еда',
        'children': [
            {'name': 'Мясная продукция', 'children': []},
            {'name': 'Молочная продукция', 'children': []},
            {'name': 'Кафе', 'children': []},
        ],
    },
    {
        'name': 'Автомобили',
        'children': [
            {
                'name': 'Грузовые',
                'children': [
                    {
                        'name': 'Запчасти для грузовых автомобилей',
                        'children': [],
                    }
                ],
            },
            {
                'name': 'Легковые',
                'children': [{'name': 'Аксессуары', 'children': []}],
            },
        ],
    },
    {
        'name': 'Услуги',
        'children': [
            {'name': 'Финансы', 'children': []},
            {'name': 'Логистика', 'children': []},
        ],
    },
]

BUILDINGS = [
    {
        'address': 'г. Москва, ул. Ленина 1, офис 3',
        'latitude': 55.755826,
        'longitude': 37.6173,
    },
    {
        'address': 'г. Москва, ул. Тверская 7',
        'latitude': 55.765825,
        'longitude': 37.605686,
    },
    {
        'address': 'г. Москва, ул. Арбат 12',
        'latitude': 55.752023,
        'longitude': 37.592968,
    },
    {
        'address': 'г. Москва, Ленинградский проспект 25',
        'latitude': 55.790278,
        'longitude': 37.558056,
    },
    {
        'address': 'г. Москва, проспект Мира 41',
        'latitude': 55.781778,
        'longitude': 37.633194,
    },
    {
        'address': 'г. Москва, ул. Профсоюзная 18',
        'latitude': 55.676111,
        'longitude': 37.562778,
    },
]

ORGANIZATIONS = [
    {
        'name': 'ООО "Рога и Копыта"',
        'building': 'г. Москва, ул. Ленина 1, офис 3',
        'phones': ['2-222-222', '8-923-666-13-13'],
        'activities': ['Молочная продукция', 'Мясная продукция'],
    },
    {
        'name': 'Мясной двор',
        'building': 'г. Москва, ул. Тверская 7',
        'phones': ['3-333-333'],
        'activities': ['Мясная продукция'],
    },
    {
        'name': 'Сырная карта',
        'building': 'г. Москва, проспект Мира 41',
        'phones': ['8-800-100-10-10', '8-495-100-10-10'],
        'activities': ['Молочная продукция'],
    },
    {
        'name': 'Кафе "Уют"',
        'building': 'г. Москва, ул. Арбат 12',
        'phones': ['8-495-765-43-21'],
        'activities': ['Кафе', 'Еда'],
    },
    {
        'name': 'Городское кафе',
        'building': 'г. Москва, ул. Ленина 1, офис 3',
        'phones': ['8-495-700-70-70'],
        'activities': ['Кафе'],
    },
    {
        'name': 'Грузовик Сервис',
        'building': 'г. Москва, Ленинградский проспект 25',
        'phones': ['8-495-111-11-11', '8-495-222-22-22'],
        'activities': ['Грузовые'],
    },
    {
        'name': 'Грузовые запчасти',
        'building': 'г. Москва, Ленинградский проспект 25',
        'phones': ['8-495-333-33-33'],
        'activities': ['Запчасти для грузовых автомобилей'],
    },
    {
        'name': 'Легковой стиль',
        'building': 'г. Москва, ул. Профсоюзная 18',
        'phones': ['8-495-444-44-44'],
        'activities': ['Легковые'],
    },
    {
        'name': 'Автоаксессуары 24',
        'building': 'г. Москва, ул. Профсоюзная 18',
        'phones': ['8-495-555-55-55'],
        'activities': ['Аксессуары'],
    },
    {
        'name': 'Быстрые кредиты',
        'building': 'г. Москва, ул. Тверская 7',
        'phones': ['8-495-888-88-88'],
        'activities': ['Финансы', 'Услуги'],
    },
    {
        'name': 'Логистик Плюс',
        'building': 'г. Москва, проспект Мира 41',
        'phones': ['8-495-999-99-99'],
        'activities': ['Логистика'],
    },
    {
        'name': 'Фермер Центр',
        'building': 'г. Москва, ул. Арбат 12',
        'phones': ['8-495-112-23-34', '8-495-112-23-35'],
        'activities': ['Еда', 'Молочная продукция', 'Мясная продукция'],
    },
]


async def seed_database(session: AsyncSession, *, reset: bool = False) -> bool:
    if reset:
        await session.execute(delete(organization_activities))
        await session.execute(delete(OrganizationPhone))
        await session.execute(delete(Organization))
        await session.execute(delete(Activity))
        await session.execute(delete(Building))
        await session.commit()

    already_seeded = await session.scalar(select(Organization.id).limit(1))
    if already_seeded is not None:
        return False

    buildings: dict[str, Building] = {}
    for raw_building in BUILDINGS:
        building = Building(**raw_building)
        session.add(building)
        buildings[building.address] = building

    activities_by_name: dict[str, Activity] = {}
    for raw_activity in ACTIVITY_TREE:
        await _create_activity_subtree(
            session=session,
            activities_by_name=activities_by_name,
            raw_activity=raw_activity,
            parent=None,
            level=1,
        )

    for raw_organization in ORGANIZATIONS:
        organization = Organization(
            name=raw_organization['name'],
            building=buildings[raw_organization['building']],
            phones=[
                OrganizationPhone(phone=phone)
                for phone in raw_organization['phones']
            ],
            activities=[
                activities_by_name[activity_name]
                for activity_name in raw_organization['activities']
            ],
        )
        session.add(organization)

    await session.commit()
    return True


async def _create_activity_subtree(
    *,
    session: AsyncSession,
    activities_by_name: dict[str, Activity],
    raw_activity: dict,
    parent: Activity | None,
    level: int,
) -> Activity:
    if level > 3:
        raise ValueError('Activity nesting level cannot exceed 3.')

    activity = Activity(name=raw_activity['name'], parent=parent, level=level)
    session.add(activity)
    await session.flush()
    activities_by_name[activity.name] = activity

    for child in raw_activity.get('children', []):
        await _create_activity_subtree(
            session=session,
            activities_by_name=activities_by_name,
            raw_activity=child,
            parent=activity,
            level=level + 1,
        )
    return activity


async def _seed_from_cli(reset: bool) -> bool:
    async with SessionLocal() as session:
        return await seed_database(session, reset=reset)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    parser = argparse.ArgumentParser(
        description='Seed the database with demo data.'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Delete existing data before seeding.',
    )
    args = parser.parse_args()

    inserted = asyncio.run(_seed_from_cli(reset=args.reset))
    logger.info(
        'Seed completed.' if inserted else 'Seed skipped: data already exists.'
    )
