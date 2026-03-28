from pydantic import BaseModel
from datetime import date 


class EpuisesUpdate(BaseModel):
    series: str|None= None
    nature:str|None= None
    
class RapportEpuises(BaseModel):
     date_debut: date
     date_fin: date 