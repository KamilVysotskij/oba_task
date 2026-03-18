from app.api.schemas.activities import ActivityRead, ActivityTreeNode
from app.repositories.activity import ActivityRepository


class ActivityService:
    def __init__(self, activities: ActivityRepository) -> None:
        self.activities = activities

    async def list_activities(self) -> list[ActivityRead]:
        return [
            ActivityRead.model_validate(activity)
            for activity in await self.activities.list_all()
        ]

    async def get_tree(self) -> list[ActivityTreeNode]:
        activities = await self.activities.list_all()
        nodes = {
            activity.id: ActivityTreeNode(
                id=activity.id, name=activity.name, level=activity.level
            )
            for activity in activities
        }
        roots: list[ActivityTreeNode] = []
        for activity in activities:
            node = nodes[activity.id]
            if activity.parent_id is None:
                roots.append(node)
                continue
            nodes[activity.parent_id].children.append(node)
        self._sort_tree(roots)
        return roots

    def _sort_tree(self, nodes: list[ActivityTreeNode]) -> None:
        nodes.sort(key=lambda item: (item.level, item.name.lower(), item.id))
        for node in nodes:
            self._sort_tree(node.children)
