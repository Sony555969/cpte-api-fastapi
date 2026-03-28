from pydantic import BaseModel

class Entree_validation(BaseModel):
    detail_id: int
    quantite_validee: int
    valide_par: str