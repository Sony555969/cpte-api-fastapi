from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Notification(SQLModel, table= True):
      id: Optional[int]= Field(default= None, primary_key= True)
      destinataire: str
      message: str
      lu: bool= Field(default= False)
      date_envoi: datetime= Field(default_factory= datetime.now)