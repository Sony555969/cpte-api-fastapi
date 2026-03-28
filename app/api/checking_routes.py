import os
from dotenv import load_dotenv
from app.core.db import get_session
from app.models.imprime_val import Imprime_valeur,ScanLog
from app.schemas.checking_out import DocumentOut,CheckRequest,QRData,QRRequest
from app.core.security import generate_signature,decrypt_payload
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session,select
from datetime import datetime,date
import json, base64 
from Crypto.Cipher import AES 
from Crypto.Random import get_random_bytes
import qrcode
import re
from app.models.details_carnets import Details_Carnets
from app.models.demande import Demande
from sqlalchemy import select



router_qr = APIRouter(prefix="/qrcode", tags=["qrcode"])
router_verifier = APIRouter(prefix="/verifier", tags=["verifier"])

# ⚠️ Clé AES à garder secrète (32 bytes pour AES-256) 
load_dotenv()
key_str = os.environ.get("AES_SECRET_KEY") 

if not key_str: 
    raise RuntimeError("La variable AES_SECRET_KEY n'est pas définie dans .env") 
SECRET_KEY_AES = key_str.encode("utf-8") # 32 bytes pour AES-256
#STATIC_DIR = "static/qrcodes"
BASE_DIR = "C:/qrcodes"
#Avec chiffremnt

@router_qr.post("/generate") 
def generate_qr_payload(data: QRData , session: Session = Depends(get_session)): 
    
    try: 
       
        # Générer la signature côté serveur 
        sig = generate_signature(data.numero)
        
        # 1. Sérialiser en texte JSON 
        payload = { 
                   "numero": data.numero, 
                   "sig": sig, 
                   "ts": data.ts 
                   }
       
        plaintext = json.dumps(payload).encode("utf-8") 
       
        # 2. Créer un chiffreur AES en mode GCM 
        cipher = AES.new(SECRET_KEY_AES, AES.MODE_GCM) 
        ciphertext, tag = cipher.encrypt_and_digest(plaintext) 
        
        # 3. Construire le paquet chiffré 
        encrypted_payload = { 
                             "nonce": base64.b64encode(cipher.nonce).decode("utf-8"), 
                             "tag": base64.b64encode(tag).decode("utf-8"),
                             "ciphertext": base64.b64encode(ciphertext).decode("utf-8") 
        }
       
        # 3. Enregistrer dans la base 
        imprime = Imprime_valeur( 
                                 numero=data.numero, 
                                 nature=data.nature, 
                                 date_emission=datetime.now(), 
                                 statut="VALIDE",
                                 signature= sig
                                 ) 
    
        session.add(imprime) 
        session.commit()
        
        # 5. Générer le QR code à partir du paquet chiffré 
    
        qr = qrcode.make(json.dumps(encrypted_payload)) 
        
        now = datetime.now() 
        year = now.strftime("%Y") 
        month = now.strftime("%m") 
        dirpath = os.path.join(BASE_DIR, year, month) 
        os.makedirs(dirpath, exist_ok=True)
        
        # buffer = io.BytesIO() 
        # qr.save(buffer, format="PNG") 
        # img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
        # Créer un nom de fichier unique 
        filename = f"{data.numero}_{int(datetime.now().timestamp())}.png" 
        filepath = os.path.join(dirpath, filename)
        
        # Sauvegarder le fichier 
        #os.makedirs(STATIC_DIR, exist_ok=True) 
        qr.save(filepath)
        
        # 6. Retourner l'image encodée en base64 
        # return { 
        #          "qr_url": f"data:image/png;base64,{img_str}", 
        #          "encrypted_payload": encrypted_payload 
        #          }
        
        # Retourner l’URL publique 
         
        return { 
                "qr_url": f"/qrcodes/{year}/{month}/{filename}", 
                "encrypted_payload": encrypted_payload
                }
        
    except Exception as e: 
        raise HTTPException(status_code=500, detail="Erreur lors du chiffrement")

# ----------------------------- # Router pour vérification # -----------------------------


@router_verifier.post("/check") 
def verify(request: QRRequest, session: Session = Depends(get_session)): 
        
    try:         
        # Déchiffrement du contenu du QR code 
      
        decrypted = decrypt_payload(request.nonce, request.tag, request.ciphertext)
                     
        payload = json.loads(decrypted.decode("utf-8"))        
        code = payload["numero"] 
        sig = payload["sig"] 
        ts = payload["ts"] 
        agent = request.agent 
       
    except Exception as e: 
        raise HTTPException(status_code=400, detail={"status": "INVALID", "reason": "QR CODE NON VALIDE"})
    
    # Vérification en base 
    imprime = session.query(Imprime_valeur).filter(Imprime_valeur.numero == code).first() 
    
    if not imprime: 
        raise HTTPException(status_code=404, detail={"status": "INVALID", "reason": "NUMERO INCONNU"}) 
    
    expected = generate_signature(code) 
    
    if expected != sig: 
        raise HTTPException(status_code=403, detail={"status": "FRAUD", "reason": "SIGNATURE INVALIDE"}) 
    
    if imprime.statut != "VALIDE": 
        raise HTTPException(status_code=409, detail={"status": "INVALID", "reason": f"STATUT {imprime.valid}"}) 
   
    # Log du scan 
    log = ScanLog(numero=code, agent=agent, date_scan=datetime.now()) 
    
    session.add(log) 
    session.commit()
    
    # Compter et récupérer les derniers scans 
    scan_count = session.query(ScanLog).filter(ScanLog.numero == code).count() 
    last_scans = ( 
                  session.query(ScanLog) 
                  .filter(ScanLog.numero == code) 
                  .order_by(ScanLog.date_scan.desc()) 
                  .limit(5) 
                  .all() 
                  ) 
    
    
    # Récupérer le service demandeur
    stmt = (
    select(Demande)
    .join(Details_Carnets, Demande.id == Details_Carnets.demande_id)
    .where(Details_Carnets.nature == imprime.nature)
    .where(Details_Carnets.series == code[2:])
    .where(Details_Carnets.statut.in_(["distribuee", "epuise"]))
)

    resultat = session.scalars(stmt).first()
  
    
    return { 
            "valid": True, 
            "data":{
            "Numero":re.sub(r'^[A-Z]+','',imprime.numero), 
            "Nature": imprime.nature, 
            "ts": imprime.date_emission, 
            "scan_count": scan_count, "last_scans": [{"agent": s.agent, "date_scan": s.date_scan} for s in last_scans],
            "demandeur":  resultat.demandeur,
            "date_demande": resultat.date_demande.date()
            }

            } 
            
            
