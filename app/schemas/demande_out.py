from pydantic import BaseModel
from datetime import date

class Demande_out(BaseModel):
    email: str 
    demandeur: str 
    quantity: int
    date_dmde: date
    nature: str
    qte_dmde: int
    id:int
  