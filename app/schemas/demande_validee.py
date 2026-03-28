from pydantic import BaseModel
from typing import List
from app.schemas.entree_validation import Entree_validation


class Demande_validee(BaseModel):  
    validations: List[Entree_validation]