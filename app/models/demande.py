from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional



class Demande(SQLModel, table=True):
    id: Optional[int]= Field(default= None, primary_key=True)
    demandeur: str
    demandeur_email: str
    date_demande: datetime= Field(default_factory=datetime.now)
    statut: str=  Field(default="en_attente") 