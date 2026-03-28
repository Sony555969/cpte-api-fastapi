from pydantic import BaseModel

class Demandeurs(BaseModel):
    demandeur: str
    email: str 