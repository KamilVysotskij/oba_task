from fastapi import APIRouter, Depends

from app.api.dependencies import get_building_service_dep
from app.api.schemas.buildings import BuildingRead
from app.core.security import require_api_key

router = APIRouter(
    prefix='/buildings',
    tags=['Buildings'],
    dependencies=[Depends(require_api_key)],
)


@router.get(
    '',
    response_model=list[BuildingRead],
    summary='Получить список зданий',
)
async def list_buildings(
    service: get_building_service_dep,
) -> list[BuildingRead]:
    return await service.list_buildings()
