from datetime import UTC, datetime
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator
)


class ActivitySessionIngest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    collector_event_id: UUID

    executable_name: str = Field(
        min_length=1,
        max_length=255
    )

    display_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255
    )

    started_at: AwareDatetime
    ended_at: AwareDatetime


    @field_validator("executable_name", mode="before")
    @classmethod
    def normalize_executable_name(cls, value):
        if isinstance(value, str):
            if any(separator in value for separator in ("/", "\\", ":")):
                raise ValueError("Provide an executable name, not a path")

            return value.lower()

        return value