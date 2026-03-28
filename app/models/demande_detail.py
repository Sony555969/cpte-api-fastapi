from sqlmodel import SQLModel, Field
from typing import Optional


class Demande_Detail(SQLModel, table= True):
    did: Optional[int]= Field(default= None, primary_key= True)
    demande_id: int= Field(foreign_key= "demande.id")
    nature: int= Field(foreign_key="stock_carnet.nature")
    quantite_demandee: int
    quantite_disponible: int
    quantite_validee: int= 0
    statut: str= Field(default="en_attente")