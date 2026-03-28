from fastapi import APIRouter, Depends, HTTPException, Response,BackgroundTasks
from app.core.db import get_session
from pydantic import BaseModel
from app.core.config_mail import mail_config
from app.schemas.demande_out import Demande_out
from fastapi_mail import FastMail, MessageSchema
from app.core.pdf_utils import generate_pdf_report,generate_pdf_rejected_report
import tempfile 
from pathlib import Path
import uuid



router = APIRouter(prefix="/send", tags=["send"])

@router.get("/report-pdf")
async def report_pdf(demande: Demande_out):
   
  
    pdf_bytes = generate_pdf_report(demande) 
    return Response( 
            content=pdf_bytes, media_type="application/pdf", 
            headers={ 
                         "Content-Disposition": "inline; filename=validation_iv.pdf" 
            } 
    )
    
@router.post("/demande-pdf")
async def send_demande_report(demande: Demande_out, background_tasks: BackgroundTasks):
    
    pdf_bytes = generate_pdf_report(demande)
    
    # Sauvegarde temporaire du PDF 
    tmp_file = Path(tempfile.gettempdir()) / f"validation_demande_{uuid.uuid4()}.pdf" 
    with open(tmp_file, "wb") as f: 
        f.write(pdf_bytes) # Ici, attachments attend un chemin de fichier 
        
   
    message = MessageSchema(
        subject="Rapport de demande - Imprimés de valeur",
        recipients=[demande.email],
        body=f"""
Bonjour {demande.demandeur},

Veuillez trouver ci-joint votre rapport concernant la demande d’imprimés de valeur du {demande.date_dmde}.


Cordialement,
La Direction.
""",
        subtype="plain",   # ✅ OBLIGATOIRE
        attachments=[str(tmp_file)]
    )

    
    fm = FastMail(mail_config) 
    background_tasks.add_task(fm.send_message, message) 
    
    return {"success": True}


@router.post("/demande-rejected-pdf")
async def send_demande_report(demande: Demande_out, background_tasks: BackgroundTasks):
    
    pdf_bytes = generate_pdf_rejected_report(demande)
    
    # Sauvegarde temporaire du PDF 
    tmp_file = Path(tempfile.gettempdir()) / f"rejet_demande_{uuid.uuid4()}.pdf" 
    with open(tmp_file, "wb") as f: 
        f.write(pdf_bytes) # Ici, attachments attend un chemin de fichier 
        
   
    message = MessageSchema(
        subject="Rapport de demande - Imprimés de valeur",
        recipients=[demande.email],
        body=f"""
Bonjour {demande.demandeur},

Veuillez trouver ci-joint votre rapport concernant la demande d’imprimés de valeur du {demande.date_dmde}.


Cordialement,
La Direction.
""",
        subtype="plain",   # ✅ OBLIGATOIRE
        attachments=[str(tmp_file)]
    )

    
    fm = FastMail(mail_config) 
    background_tasks.add_task(fm.send_message, message) 
    
    return {"success": True}

async def send_and_delete(fm, message, path):
    await fm.send_message(message)
    if path.exists():
        path.unlink()