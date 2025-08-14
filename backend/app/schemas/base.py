"""Base Pydantic schemas"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamps"""
    created_at: datetime
    updated_at: Optional[datetime] = None
