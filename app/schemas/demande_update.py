from pydantic import BaseModel
from typing import Optional



class Demande_update(BaseModel):
    qte_validee : Optional[str]=None
    statut : Optional[str]=None
    date_validation : Optional[str]=None
    valide_par : Optional[str]=None
    commentaire: Optional[str]=None