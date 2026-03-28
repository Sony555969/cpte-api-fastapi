from pydantic import BaseModel
from typing import List
from app.schemas.demandeurs import Demandeurs
from app.schemas.item import Item

class Details_demandes_update(BaseModel):
    demandeurs: Demandeurs    
    details: List[Item]