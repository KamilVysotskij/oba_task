from fastapi import APIRouter, Depends

from app.api.dependencies import get_activity_service_dep
from app.api.schemas.activities import ActivityRead, ActivityTreeNode
from app.core.security import require_api_key

router = APIRouter(
    prefix='/activities',
    tags=['Activities'],
    dependencies=[Depends(require_api_key)],
)


@router.get(
    '',
    response_model=list[ActivityRead],
    summary='Получить список деятельностей',
)
async def list_activities(
    service: get_activity_service_dep,
) -> list[ActivityRead]:
    return await service.list_activities()


@router.get(
    '/tree',
    response_model=list[ActivityTreeNode],
    summary='Получить дерево деятельностей',
)
async def get_activity_tree(
    service: get_activity_service_dep,
) -> list[ActivityTreeNode]:
    return await service.get_tree()
