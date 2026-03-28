from pydantic import BaseModel
from typing import List
from datetime import date
#
#class Distribution_update(BaseModel):        
#    distributions: List[Entree_distribution]
    
    
class vueDistribuee(BaseModel):
    demandeur: str
    nature: str
    statut: str
    date_epuise: date
    