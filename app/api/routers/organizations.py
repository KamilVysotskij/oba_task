from fastapi import APIRouter, Depends, Path, Query

from app.api.dependencies import get_organization_query_service_dep
from app.api.schemas.organizations import OrganizationRead
from app.core.security import require_api_key

router = APIRouter(
    prefix='/organizations',
    tags=['Organizations'],
    dependencies=[Depends(require_api_key)],
)


@router.get(
    '/by-building/{building_id}',
    response_model=list[OrganizationRead],
    summary='Получить организации по зданию',
)
async def list_organizations_by_building(
    building_id: int = Path(..., gt=0),
    *,
    service: get_organization_query_service_dep,
) -> list[OrganizationRead]:
    return await service.list_by_building(building_id)


@router.get(
    '/by-activity',
    response_model=list[OrganizationRead],
    summary='Получить организации по виду деятельности и вложенным видам',
)
async def list_organizations_by_activity(
    name: str = Query(
        ...,
        min_length=1,
        description=(
            'Название вида деятельности. Поиск автоматически включает '
            'все вложенные деятельности.'
        ),
    ),
    *,
    service: get_organization_query_service_dep,
) -> list[OrganizationRead]:
    return await service.list_by_activity(name)


@router.get(
    '/search/name',
    response_model=list[OrganizationRead],
    summary='Поиск организаций по названию',
)
async def search_organizations_by_name(
    q: str = Query(
        ..., min_length=1, description='Часть названия организации.'
    ),
    *,
    service: get_organization_query_service_dep,
) -> list[OrganizationRead]:
    return await service.search_by_name(q)


@router.get(
    '/search/geo/radius',
    response_model=list[OrganizationRead],
    summary='Поиск организаций в радиусе от точки',
)
async def search_organizations_in_radius(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_m: float = Query(..., gt=0, le=100_000),
    *,
    service: get_organization_query_service_dep,
) -> list[OrganizationRead]:
    return await service.list_in_radius(
        latitude=latitude, longitude=longitude, radius_m=radius_m
    )


@router.get(
    '/search/geo/box',
    response_model=list[OrganizationRead],
    summary='Поиск организаций в прямоугольной области',
)
async def search_organizations_in_box(
    min_latitude: float = Query(..., ge=-90, le=90),
    max_latitude: float = Query(..., ge=-90, le=90),
    min_longitude: float = Query(..., ge=-180, le=180),
    max_longitude: float = Query(..., ge=-180, le=180),
    *,
    service: get_organization_query_service_dep,
) -> list[OrganizationRead]:
    return await service.list_in_box(
        min_latitude=min_latitude,
        max_latitude=max_latitude,
        min_longitude=min_longitude,
        max_longitude=max_longitude,
    )


@router.get(
    '/{organization_id}',
    response_model=OrganizationRead,
    summary='Получить организацию по идентификатору',
)
async def get_organization(
    organization_id: int = Path(..., gt=0),
    *,
    service: get_organization_query_service_dep,
) -> OrganizationRead:
    return await service.get_by_id(organization_id)
