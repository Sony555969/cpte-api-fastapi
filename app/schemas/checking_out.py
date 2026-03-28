from pydantic import BaseModel
from datetime import date

class DocumentOut(BaseModel): 
    numero_doc: str 
    nature: str 
    date_emission: date 
    valide: bool 
    
class Config: 
    orm_mode = True


class CheckRequest(BaseModel): 
    code: str 
    sig: str 
    agent: str = "unknown"
    


class QRRequest(BaseModel):
    nonce: str
    tag: str
    ciphertext: str
    agent: str 
 
class QRData(BaseModel): 
    numero: str     
    ts: str 
    nature: str