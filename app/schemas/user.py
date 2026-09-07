from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True) # lets pydantic read objects from a sqlalchemy model

    id: UUID
    email: EmailStr
    reporting_timezone: str
    created_at: datetime # account creation date