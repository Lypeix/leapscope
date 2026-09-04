from typing import Annotated
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator
)

NormalizedEmail = Annotated[EmailStr, AfterValidator(str.lower)]

class UserRegister(BaseModel):
    model_config = ConfigDict(extra="forbid") # helps catch unexpected input

    email: NormalizedEmail = Field(max_length=300)
    password: SecretStr = Field(min_length=10, max_length=100)
    reporting_timezone: str = Field(default="UTC", max_length=70)

    @field_validator("reporting_timezone")
    @classmethod
    def validate_reporting_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError,ValueError) as error:
            raise ValueError(
                "Timezone not found"
            ) from error
        return value


class UserLogin(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: NormalizedEmail = Field(max_length=300)
    password: SecretStr = Field(min_length=10, max_length=100)