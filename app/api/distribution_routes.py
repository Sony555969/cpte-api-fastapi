from fastapi import APIRouter, Depends, HTTPException
from app.core.db import get_session
from sqlmodel import Session,select,update,or_
from app.models.demande_detail import Demande_Detail
from app.models.demande import Demande
from app.models.enums import StatutValidation
from datetime import datetime

router = APIRouter(prefix="/distribution", tags=["distribution"])


@router.patch("/{demande_id}")
def distribuer_commande(demande_id: int,                                   
               session: Session= Depends(get_session)):
    
    details= session.exec(select(Demande_Detail)
                          .where(Demande_Detail.did== demande_id)
                          ).first()
    
    demande= session.exec(select(Demande)
                          .filter(Demande.id== details.demande_id)
                          ).first()
    if not demande:
        HTTPException(status_code=404, detail= "Demande introuvable")

    
    session.exec(
        update(Demande_Detail)
        .where(Demande_Detail.did== demande_id,
            or_( Demande_Detail.statut== StatutValidation.validee,
                Demande_Detail.statut== StatutValidation.partiellement_validee
                )
        )
        .values(statut="distribuee")
    )       
    session.commit()
    
    demande.statut= StatutValidation.distribuee
    
    session.add(demande)
    session.commit()
    session.refresh(demande)
   
    
    return {"message": "Commande distribuée !"}  


@router.patch("/carnet")
def distribuer_commande(demande_id: int,                                   
               session: Session= Depends(get_session)):
    
    details= session.exec(select(Demande_Detail)
                          .where(Demande_Detail.did== demande_id)
                          ).first()
    
    demande= session.exec(select(Demande)
                          .filter(Demande.id== details.demande_id)
                          ).first()
    if not demande:
        HTTPException(status_code=404, detail= "Demande introuvable")

    
    session.exec(
        update(Demande_Detail)
        .where(Demande_Detail.did== demande_id,
            or_( Demande_Detail.statut== StatutValidation.validee,
                Demande_Detail.statut== StatutValidation.partiellement_validee
                )
        )
        .values(statut="distribuee")
    )       
    session.commit()
    
    demande.statut= StatutValidation.distribuee
    
    session.add(demande)
    session.commit()
    session.refresh(demande)
   
    
    return {"message": "Commande distribuée !"}  