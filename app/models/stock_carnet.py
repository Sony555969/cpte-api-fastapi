from sqlmodel import SQLModel, Field
from typing import Optional

class Stock_Carnet(SQLModel, table = True):
    id: Optional[int]= Field(default= None, primary_key= True)
    nature: str   
    quantite_disponible: int= 0 
    numero_serie_debut: Optional[str]=None
    numero_serie_fin: Optional[str]=None  
    taille_carnet : Optional[int] = 50
    statut: Optional[str] =Field(default="disponible")
    
