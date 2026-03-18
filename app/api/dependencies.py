from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.repositories.activity import ActivityRepository
from app.repositories.building import BuildingRepository
from app.repositories.organization import OrganizationRepository
from app.services.activity_service import ActivityService
from app.services.building_service import BuildingService
from app.services.organization_query_service import OrganizationQueryService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


get_db_session_dep = Annotated[AsyncSession, Depends(get_db_session)]


async def get_organization_query_service(
    session: get_db_session_dep,
) -> OrganizationQueryService:
    return OrganizationQueryService(
        organizations=OrganizationRepository(session),
        buildings=BuildingRepository(session),
        activities=ActivityRepository(session),
    )


get_organization_query_service_dep = Annotated[
    OrganizationQueryService,
    Depends(get_organization_query_service),
]


async def get_building_service(
    session: get_db_session_dep,
) -> BuildingService:
    return BuildingService(buildings=BuildingRepository(session))


get_building_service_dep = Annotated[
    BuildingService,
    Depends(get_building_service),
]


async def get_activity_service(
    session: get_db_session_dep,
) -> ActivityService:
    return ActivityService(activities=ActivityRepository(session))


get_activity_service_dep = Annotated[
    ActivityService,
    Depends(get_activity_service),
]
