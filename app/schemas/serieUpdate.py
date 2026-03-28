from pydantic import BaseModel

class SerieUpdate(BaseModel):
    nature: str
    series: str