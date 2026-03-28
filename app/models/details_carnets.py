
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date

    
class Details_Carnets(SQLModel, table = True):
    id : Optional[int]= Field(default=None, primary_key=True)
    stock_id: int     
    series : str
    nature: str
    statut : str = Field(default="disponible")
    demande_id: int 
    distribution_id: int
    date_epuise: date