from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

      
class Distribution(SQLModel, table= True):
      id: Optional[int]= Field(default= None, primary_key= True)
      demande_id: int= Field(foreign_key="demande.id")
      quantite: int
      distribue_par: str
      date_distribution: datetime= Field(default_factory=datetime.now)
      
      

      