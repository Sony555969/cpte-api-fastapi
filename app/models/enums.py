from sqlalchemy import Enum


class StatutValidation(str, Enum):
    en_attente= "en_attente"
    validee= "validee"   
    rejetee= "rejetee"
    distribuee= "distribuee"
    disponible= "disponible"
    epuise="epuise"
    partiellement_validee= "partiellement_validee"