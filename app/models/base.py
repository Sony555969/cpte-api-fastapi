from sqlmodel import SQLModel, Field
from datetime import datetime

class BaseModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now, index=True)
    updated_at: datetime = Field(default_factory=datetime.now)
