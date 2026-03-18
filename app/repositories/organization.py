import math

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Activity, Building, Organization

EARTH_RADIUS_KM = 6371.0


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, organization_id: int) -> Organization | None:
        statement = self._base_statement().where(
            Organization.id == organization_id
        )
        return await self.session.scalar(statement)

    async def list_by_building(self, building_id: int) -> list[Organization]:
        statement = (
            self._base_statement()
            .where(Organization.building_id == building_id)
            .order_by(Organization.id)
        )
        return await self._execute(statement)

    async def list_by_activity_ids(
        self, activity_ids: list[int]
    ) -> list[Organization]:
        if not activity_ids:
            return []
        statement = (
            self._base_statement()
            .join(Organization.activities)
            .where(Activity.id.in_(activity_ids))
            .distinct()
            .order_by(Organization.id)
        )
        return await self._execute(statement)

    async def search_by_name(self, query: str) -> list[Organization]:
        statement = (
            self._base_statement()
            .where(Organization.name.ilike(f'%{query.strip()}%'))
            .order_by(Organization.name, Organization.id)
        )
        return await self._execute(statement)

    async def list_in_box(
        self,
        *,
        min_latitude: float,
        max_latitude: float,
        min_longitude: float,
        max_longitude: float,
    ) -> list[Organization]:
        statement = (
            self._base_statement()
            .join(Organization.building)
            .where(
                Building.latitude.between(min_latitude, max_latitude),
                Building.longitude.between(min_longitude, max_longitude),
            )
            .order_by(Organization.id)
        )
        return await self._execute(statement)

    async def list_in_radius(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_m: float,
    ) -> list[Organization]:
        radius_km = radius_m / 1000
        latitude_delta = math.degrees(radius_km / EARTH_RADIUS_KM)
        longitude_delta = latitude_delta / max(
            math.cos(math.radians(latitude)), 0.01
        )
        distance_expression = EARTH_RADIUS_KM * func.acos(
            func.least(
                1.0,
                func.greatest(
                    -1.0,
                    func.cos(func.radians(latitude))
                    * func.cos(func.radians(Building.latitude))
                    * func.cos(
                        func.radians(Building.longitude)
                        - func.radians(longitude)
                    )
                    + func.sin(func.radians(latitude))
                    * func.sin(func.radians(Building.latitude)),
                ),
            ),
        )
        statement = (
            self._base_statement()
            .join(Organization.building)
            .where(
                Building.latitude.between(
                    latitude - latitude_delta, latitude + latitude_delta
                ),
                Building.longitude.between(
                    longitude - longitude_delta, longitude + longitude_delta
                ),
                distance_expression <= radius_km,
            )
            .order_by(distance_expression, Organization.id)
        )
        return await self._execute(statement)

    def _base_statement(self) -> Select[tuple[Organization]]:
        return select(Organization).options(
            selectinload(Organization.building),
            selectinload(Organization.phones),
            selectinload(Organization.activities),
        )

    async def _execute(
        self, statement: Select[tuple[Organization]]
    ) -> list[Organization]:
        result = await self.session.scalars(statement)
        return list(result.unique().all())
