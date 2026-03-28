from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Imprime_valeur(SQLModel,table=True):   

    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(sa_column_kwargs={"unique": True}, max_length=25, nullable=False)
    nature: str = Field(nullable=False, max_length=100)
    date_emission: datetime=Field(default= datetime.now)
    signature : str
    statut :str= Field(default="VALIDE")  # VALIDE / ANNULEE / EXPIREE
    

class ScanLog(SQLModel,table=True):
    __tablename__ = "scans"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    numero :str
    agent :str
    date_scan: datetime = Field(default_factory=datetime.now)
    
