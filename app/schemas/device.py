from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class DeviceRegister(BaseModel): # describes the accepted payload
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    name: str = Field(min_length=1, max_length=100)

class DeviceRead(BaseModel): # describes the response / schema user has to fill in
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    user_id: UUID
    name: str
    created_at: datetime
