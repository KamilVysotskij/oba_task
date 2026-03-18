from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Building


class BuildingRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Building]:
        statement = select(Building).order_by(Building.address)
        result = await self.session.scalars(statement)
        return list(result.all())

    async def get_by_id(self, building_id: int) -> Building | None:
        statement = select(Building).where(Building.id == building_id)
        return await self.session.scalar(statement)
