from app.core.db import get_session
from sqlmodel import Session,select,and_
from fastapi import APIRouter, Depends, HTTPException
from app.models.details_carnets import Details_Carnets
from app.schemas.serieUpdate import SerieUpdate
from app.models.enums import StatutValidation
from datetime import date


router = APIRouter(prefix="/carnets", tags=["carnets"])

@router.post("/{serie}/epuiser")
def distribuer(serie: str,                          
               session: Session= Depends(get_session)):
    statement = select(Details_Carnets).where(Details_Carnets.series==serie)
    result = session.exec(statement)
    carnet = result.first()
    
    if not carnet:
        raise HTTPException(404, "Carnet non trouvé")      
    carnet.statut= "epuise"
   
   
    session.add(carnet)        
    session.commit()
    return {"message":f"Le carnet {carnet.series}  a été épuisé avec succès !"}
     


    
@router.patch("/{demande_id}/epuises")
def distribuer_commande(demande_id: int,
               series: SerieUpdate,                             
               session: Session= Depends(get_session)):
  
    carnet= session.exec(select(Details_Carnets)
                          .where(and_(Details_Carnets.demande_id== demande_id, Details_Carnets.series== series.series))
                          ).first()
    if not carnet:
        HTTPException(status_code=404, detail= "Série introuvable")
    carnet.date_epuise= date.today()
    carnet.statut= StatutValidation.epuise  
    
    session.add(carnet)
    session.commit()
    session.refresh(carnet)  
    
    return {"message": "Carnet epuisé!"}     



    
