from sqlmodel import SQLModel
from datetime import datetime



class Carnet_distribue_service(SQLModel):
    id: int
    demandeur: str
    demandeur_email: str
    nature: str
    quantite_validee: int
    date_demande: datetime