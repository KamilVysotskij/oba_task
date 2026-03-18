from app.api.schemas.buildings import BuildingRead
from app.repositories.building import BuildingRepository


class BuildingService:
    def __init__(self, buildings: BuildingRepository) -> None:
        self.buildings = buildings

    async def list_buildings(self) -> list[BuildingRead]:
        return [
            BuildingRead.model_validate(building)
            for building in await self.buildings.list_all()
        ]
