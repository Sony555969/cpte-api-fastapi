from sqlmodel import SQLModel, Field
from typing import Optional



class Stock(SQLModel,table= True):
    id: Optional[int]= Field(default= None, primary_key= True)
    stock_carnet_id : Optional[int]
    nature : str
    quantite_disponible: int
    statut: str