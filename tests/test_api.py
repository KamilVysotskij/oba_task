import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import (
    get_activity_id,
    get_building_id,
    get_organization_id,
)

API_KEY_HEADER = {'X-API-Key': 'dev-api-key'}
pytestmark = pytest.mark.anyio


def _collect_tree_depth(nodes: list[dict], depth: int = 1) -> int:
    if not nodes:
        return depth - 1
    return max(
        _collect_tree_depth(node['children'], depth + 1) for node in nodes
    )


async def test_requires_api_key(client: AsyncClient) -> None:
    response = await client.get('/api/v1/buildings')

    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid or missing API key.'}


async def test_get_organization_by_id(
    client: AsyncClient,
    seeded_session: AsyncSession,
) -> None:
    organization_id = await get_organization_id(
        seeded_session, 'ООО "Рога и Копыта"'
    )

    response = await client.get(
        f'/api/v1/organizations/{organization_id}', headers=API_KEY_HEADER
    )

    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'ООО "Рога и Копыта"'
    assert data['building']['address'] == 'г. Москва, ул. Ленина 1, офис 3'
    assert sorted(data['phones']) == ['2-222-222', '8-923-666-13-13']


async def test_list_organizations_by_building(
    client: AsyncClient,
    seeded_session: AsyncSession,
) -> None:
    building_id = await get_building_id(
        seeded_session, 'г. Москва, ул. Ленина 1, офис 3'
    )

    response = await client.get(
        f'/api/v1/organizations/by-building/{building_id}',
        headers=API_KEY_HEADER,
    )

    assert response.status_code == 200
    names = {item['name'] for item in response.json()}
    assert names == {'ООО "Рога и Копыта"', 'Городское кафе'}


async def test_search_activity_by_name_includes_descendants(
    client: AsyncClient,
) -> None:
    response = await client.get(
        '/api/v1/organizations/by-activity',
        params={'name': 'Еда'},
        headers=API_KEY_HEADER,
    )

    assert response.status_code == 200
    names = {item['name'] for item in response.json()}
    assert 'ООО "Рога и Копыта"' in names
    assert 'Кафе "Уют"' in names
    assert 'Городское кафе' in names
    assert 'Фермер Центр' in names


async def test_list_organizations_by_exact_activity_id(
    client: AsyncClient,
    seeded_session: AsyncSession,
) -> None:
    activity_id = await get_activity_id(seeded_session, 'Грузовые')

    response = await client.get(
        f'/api/v1/organizations/by-activity/{activity_id}',
        headers=API_KEY_HEADER,
    )

    assert response.status_code == 200
    names = {item['name'] for item in response.json()}
    assert names == {'Грузовик Сервис'}


async def test_search_nested_activity_by_name_includes_descendants(
    client: AsyncClient,
) -> None:
    response = await client.get(
        '/api/v1/organizations/by-activity',
        params={'name': 'грузовые'},
        headers=API_KEY_HEADER,
    )

    assert response.status_code == 200
    names = {item['name'] for item in response.json()}
    assert names == {'Грузовик Сервис', 'Грузовые запчасти'}


async def test_search_organizations_in_radius(
    client: AsyncClient,
) -> None:
    response = await client.get(
        '/api/v1/organizations/search/geo/radius',
        params={
            'latitude': 55.755826,
            'longitude': 37.6173,
            'radius_m': 100,
        },
        headers=API_KEY_HEADER,
    )

    assert response.status_code == 200
    names = {item['name'] for item in response.json()}
    assert names == {'ООО "Рога и Копыта"', 'Городское кафе'}


async def test_search_organizations_in_box(
    client: AsyncClient,
) -> None:
    response = await client.get(
        '/api/v1/organizations/search/geo/box',
        params={
            'min_latitude': 55.676,
            'max_latitude': 55.6762,
            'min_longitude': 37.5627,
            'max_longitude': 37.5629,
        },
        headers=API_KEY_HEADER,
    )

    assert response.status_code == 200
    names = {item['name'] for item in response.json()}
    assert names == {'Легковой стиль', 'Автоаксессуары 24'}


async def test_search_organizations_by_name(
    client: AsyncClient,
) -> None:
    response = await client.get(
        '/api/v1/organizations/search/name',
        params={'q': 'афе'},
        headers=API_KEY_HEADER,
    )

    assert response.status_code == 200
    names = {item['name'] for item in response.json()}
    assert names == {'Кафе "Уют"', 'Городское кафе'}


async def test_list_buildings(client: AsyncClient) -> None:
    response = await client.get('/api/v1/buildings', headers=API_KEY_HEADER)

    assert response.status_code == 200
    addresses = {item['address'] for item in response.json()}
    assert addresses == {
        'г. Москва, ул. Ленина 1, офис 3',
        'г. Москва, ул. Тверская 7',
        'г. Москва, ул. Арбат 12',
        'г. Москва, Ленинградский проспект 25',
        'г. Москва, проспект Мира 41',
        'г. Москва, ул. Профсоюзная 18',
    }


async def test_list_activities(client: AsyncClient) -> None:
    response = await client.get('/api/v1/activities', headers=API_KEY_HEADER)

    assert response.status_code == 200
    data = response.json()
    names = {item['name'] for item in data}
    assert {'Еда', 'Мясная продукция', 'Автомобили', 'Логистика'} <= names
    assert max(item['level'] for item in data) == 3


async def test_get_activity_tree(client: AsyncClient) -> None:
    response = await client.get(
        '/api/v1/activities/tree', headers=API_KEY_HEADER
    )

    assert response.status_code == 200
    data = response.json()
    root_names = {item['name'] for item in data}
    assert root_names == {'Еда', 'Автомобили', 'Услуги'}

    cars_node = next(item for item in data if item['name'] == 'Автомобили')
    cars_children = {item['name'] for item in cars_node['children']}
    assert cars_children == {'Грузовые', 'Легковые'}

    trucks_node = next(
        item for item in cars_node['children'] if item['name'] == 'Грузовые'
    )
    truck_children = {item['name'] for item in trucks_node['children']}
    assert truck_children == {'Запчасти для грузовых автомобилей'}
    assert _collect_tree_depth(data) == 3
