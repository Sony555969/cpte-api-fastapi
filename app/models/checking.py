from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_doc: str = Field(sa_column_kwargs={"unique": True}, max_length=25, nullable=False)
    nature: str = Field(nullable=False, max_length=100)
    date_emission: datetime
    valide: bool
