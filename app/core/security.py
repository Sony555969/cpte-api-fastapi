# app/core/security.py
import os
from dotenv import load_dotenv
import bcrypt, jwt
from datetime import datetime, timedelta
import hmac
import hashlib
import base64
from Crypto.Cipher import AES

JWT_SECRET = "info@2025@drnoFLU"          # Mets une valeur via config/ENV
JWT_ALG = "HS256"
ACCESS_EXPIRE_MIN = 30
REFRESH_EXPIRE_DAYS = 7

load_dotenv()
key_str = os.environ.get("AES_SECRET_KEY") 

if not key_str: 
    raise RuntimeError("La variable AES_SECRET_KEY n'est pas définie dans .env") 
SECRET_KEY_AES = key_str.encode("utf-8") # 32 bytes pour AES-256


def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def verify_password(p: str, h: str) -> bool:
    return bcrypt.checkpw(p.encode(), h.encode())

def create_access_token(user_id: int, role: str, email: str | None= None):
    payload = {
        "sub": str(user_id),  # ex: {"id": 1, "role": "SUPERVISOR"}
        "role": role,  
        "email": email,      
        "type": "access",
        "exp": datetime.now() + timedelta(minutes=ACCESS_EXPIRE_MIN)
    }
    if email:
        payload["email"]=email
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def create_refresh_token(user_id: int, role: str):
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "refresh",
        "exp": datetime.now() + timedelta(days=REFRESH_EXPIRE_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])



#----------Signature qr code------------------

SECRET_KEY_SIG = b"DivInfo@2025@drnoFLU##" # 32 bytes (clé AES-256), à garder secrète
# ----------------------------- 
#  Génération de signature HMAC 
#  ----------------------------- 

def generate_signature(numero: str) -> str: 
    return hmac.new(SECRET_KEY_SIG, numero.encode("utf-8"), hashlib.sha256).hexdigest()


#----------logique de déchiffrement


def decrypt_payload(nonce_b64, tag_b64, ciphertext_b64):
    try:
      
        nonce = base64.b64decode(nonce_b64)       
        tag = base64.b64decode(tag_b64)       
        ciphertext = base64.b64decode(ciphertext_b64)        
        cipher = AES.new(SECRET_KEY_AES, AES.MODE_GCM, nonce=nonce)      
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)       
        return plaintext
    
    except ValueError:
        # Tag invalide → message corrompu ou clé incorrecte
        raise HTTPException(status_code=400, detail={"status": "INVALID", "reason": "TAG INVALIDE"})
    except Exception:
        # Autres erreurs (Base64, JSON, etc.)
        raise HTTPException(status_code=400, detail={"status": "INVALID", "reason": "QR CODE NON VALIDE"})


