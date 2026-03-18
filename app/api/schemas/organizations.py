from pydantic import BaseModel

from app.api.schemas.activities import ActivityRead
from app.api.schemas.buildings import BuildingRead
from app.db.models import Organization


class OrganizationRead(BaseModel):
    id: int
    name: str
    building: BuildingRead
    phones: list[str]
    activities: list[ActivityRead]

    @classmethod
    def from_entity(cls, organization: Organization) -> 'OrganizationRead':
        return cls(
            id=organization.id,
            name=organization.name,
            building=BuildingRead.model_validate(organization.building),
            phones=sorted(phone.phone for phone in organization.phones),
            activities=[
                ActivityRead.model_validate(activity)
                for activity in sorted(
                    organization.activities,
                    key=lambda item: (item.level, item.name.lower(), item.id),
                )
            ],
        )
