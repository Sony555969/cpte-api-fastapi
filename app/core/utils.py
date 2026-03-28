
from sqlmodel import Session
from app.core.db import get_session
from fastapi import Depends
import asyncio

from email.message import EmailMessage
import aiosmtplib

def generer_series(debut: int, fin: int, taille_carnet: int=50) -> list[str]:
    liste_series = []

    for i in range(debut, fin, taille_carnet):
        f = i + taille_carnet - 1
        if f > fin:
            # Carnet incomplet, on le marque avec un astérisque
            serie = f"{i:07d}-{fin:07d}*"
            liste_series.append(serie)
            break  # On arrête après le dernier carnet incomplet
        serie = f"{i:07d}-{f:07d}"
        liste_series.append(serie)

    return liste_series

#===============UTILITAIRES============================
#===================Endpoint pour insérer un intervalle

def insert_interval(start: int, end: int): 
    """ Insère dans la table Document tous les numéros compris entre start et end. 
    Exemple: /insert_interval/401/450 """ 
    liste_num= []
  
    for num in range(start, end + 1): 
        # Formatage avec padding (ex: 0000401) 
        numero = f"{num:07d}"
        liste_num.append(numero) 
                        
    return liste_num

def create_notification(destinataire: str, message: str,session :Session= Depends(get_session) ):
    notif= Notification(destinataire= destinataire, message= message)
    session.add(notif)
    session.commit()
    session.refresh(notif)
    
    #websocket
    asyncio.create_task(ConnectionManager.broadcast(f"Notification pour {destinataire} {message}"))
    # mail
    
    asyncio.create_task(send_email(destinataire,"Notification carnets",message)) 
    return notif

async def send_email(destinataire: str, sujet: str, contenu: str):
    message= EmailMessage()
    message["From"]= "noreply@drnoflu.com"
    message["To"]= destinataire
    message["Subject"]= sujet
    message.set_content(contenu)
    await aiosmtplib.send(message,
                          sender="directeur@drnoflu.com",
                          hostname="smtp.drnoflu.com",    # adresse du serveur smtp smtp.gmail.com
                          port=587,
                          username= "smtp_user",
                          password= "smtp_password",
                          start_tls=True)
                          
    


            
