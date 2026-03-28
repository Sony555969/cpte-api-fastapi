from pydantic import BaseModel

class Item(BaseModel):
    nature: str
    quantite: int