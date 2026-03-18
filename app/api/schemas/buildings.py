from pydantic import BaseModel, ConfigDict


class BuildingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    latitude: float
    longitude: float
