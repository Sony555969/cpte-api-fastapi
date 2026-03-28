from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Validation(SQLModel, table= True):
      id: Optional[int]= Field(default= None, primary_key= True)
      demande_detail_id: int= Field(foreign_key="demande_detail.did")
      nature: str 
      quantite_validee: int
      date_validation: datetime= Field(default_factory= datetime.now)
      valide_par: str