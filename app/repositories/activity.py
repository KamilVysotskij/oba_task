from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Activity


class ActivityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[Activity]:
        statement = select(Activity).order_by(
            Activity.level, Activity.name, Activity.id
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def get_by_id(self, activity_id: int) -> Activity | None:
        statement = select(Activity).where(Activity.id == activity_id)
        return await self.session.scalar(statement)

    async def get_descendant_ids(self, activity_id: int) -> list[int]:
        activity_tree: Select[tuple[int, int | None]] = (
            select(Activity.id, Activity.parent_id)
            .where(Activity.id == activity_id)
            .cte(name='activity_tree', recursive=True)
        )
        activity_alias = Activity.__table__.alias('activity_alias')
        activity_tree = activity_tree.union_all(
            select(activity_alias.c.id, activity_alias.c.parent_id).where(
                activity_alias.c.parent_id == activity_tree.c.id,
            )
        )
        statement = select(activity_tree.c.id)
        result = await self.session.scalars(statement)
        return list(result.all())

    async def get_descendant_ids_by_name(self, name: str) -> list[int]:
        normalized_name = name.strip().lower()
        activity_tree: Select[tuple[int, int | None]] = (
            select(Activity.id, Activity.parent_id)
            .where(func.lower(Activity.name) == normalized_name)
            .cte(name='activity_tree', recursive=True)
        )
        activity_alias = Activity.__table__.alias('activity_alias')
        activity_tree = activity_tree.union_all(
            select(activity_alias.c.id, activity_alias.c.parent_id).where(
                activity_alias.c.parent_id == activity_tree.c.id,
            )
        )
        statement = select(activity_tree.c.id).distinct()
        result = await self.session.scalars(statement)
        return list(result.all())
