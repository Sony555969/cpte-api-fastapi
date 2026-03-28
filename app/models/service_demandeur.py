from sqlmodel import SQLModel, Field
from typing import Optional

    
class Service_demandeur(SQLModel, table= True):
    id: Optional[int]= Field(default= None, primary_key= True)
    demandeur: str
    email: str