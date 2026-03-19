from app.api.schemas.organizations import OrganizationRead
from app.core.exceptions import EntityNotFoundError
from app.repositories.activity import ActivityRepository
from app.repositories.building import BuildingRepository
from app.repositories.organization import OrganizationRepository


class OrganizationQueryService:
    def __init__(
        self,
        *,
        organizations: OrganizationRepository,
        buildings: BuildingRepository,
        activities: ActivityRepository,
    ) -> None:
        self.organizations = organizations
        self.buildings = buildings
        self.activities = activities

    async def get_by_id(self, organization_id: int) -> OrganizationRead:
        organization = await self.organizations.get_by_id(organization_id)
        if organization is None:
            raise EntityNotFoundError('Organization not found.')
        return OrganizationRead.from_entity(organization)

    async def list_by_building(
        self, building_id: int
    ) -> list[OrganizationRead]:
        building = await self.buildings.get_by_id(building_id)
        if building is None:
            raise EntityNotFoundError('Building not found.')
        organizations = await self.organizations.list_by_building(building_id)
        return [
            OrganizationRead.from_entity(organization)
            for organization in organizations
        ]

    async def list_by_activity(
        self,
        activity_name: str,
    ) -> list[OrganizationRead]:
        activity_ids = await self.activities.get_descendant_ids_by_name(
            activity_name
        )
        if not activity_ids:
            raise EntityNotFoundError('Activity not found.')
        organizations = await self.organizations.list_by_activity_ids(
            activity_ids
        )
        return [
            OrganizationRead.from_entity(organization)
            for organization in organizations
        ]

    async def list_by_activity_id(
        self,
        activity_id: int,
    ) -> list[OrganizationRead]:
        activity = await self.activities.get_by_id(activity_id)
        if activity is None:
            raise EntityNotFoundError('Activity not found.')
        organizations = await self.organizations.list_by_activity_ids(
            [activity_id]
        )
        return [
            OrganizationRead.from_entity(organization)
            for organization in organizations
        ]

    async def search_by_name(self, query: str) -> list[OrganizationRead]:
        organizations = await self.organizations.search_by_name(query)
        return [
            OrganizationRead.from_entity(organization)
            for organization in organizations
        ]

    async def list_in_radius(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_m: float,
    ) -> list[OrganizationRead]:
        organizations = await self.organizations.list_in_radius(
            latitude=latitude,
            longitude=longitude,
            radius_m=radius_m,
        )
        return [
            OrganizationRead.from_entity(organization)
            for organization in organizations
        ]

    async def list_in_box(
        self,
        *,
        min_latitude: float,
        max_latitude: float,
        min_longitude: float,
        max_longitude: float,
    ) -> list[OrganizationRead]:
        min_latitude, max_latitude = sorted((min_latitude, max_latitude))
        min_longitude, max_longitude = sorted((min_longitude, max_longitude))
        organizations = await self.organizations.list_in_box(
            min_latitude=min_latitude,
            max_latitude=max_latitude,
            min_longitude=min_longitude,
            max_longitude=max_longitude,
        )
        return [
            OrganizationRead.from_entity(organization)
            for organization in organizations
        ]
