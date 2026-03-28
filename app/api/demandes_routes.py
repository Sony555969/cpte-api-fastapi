from fastapi import APIRouter, Depends, HTTPException
from app.models.demande import Demande
from app.schemas.details_demandes_update import Details_demandes_update
from app.models.stock import Stock
from app.core.db import get_session
from sqlmodel import Session,select,and_
from app.models.demande_detail import Demande_Detail
from app.models.details_carnets import Details_Carnets
from app.schemas.demande_validee import Demande_validee
from app.models.validation import Validation
from app.schemas.serieUpdate import SerieUpdate
from app.models.enums import StatutValidation
from app.models.distribution import Distribution
from sqlalchemy import and_, desc, join, or_,func
from datetime import datetime
from app.models.checking import Document
from app.core.utils import insert_interval
from datetime import date


router = APIRouter(prefix="/demandes", tags=["demandes"])


def numeros_details(begin:int, end:int):     
    return insert_interval(begin, end)

numeros=[]


@router.post("")
async def add_demande(item : Details_demandes_update,                  
               session: Session= Depends(get_session)):
    
    natures=[]
    
    demande = Demande(demandeur= item.demandeurs.demandeur, demandeur_email= item.demandeurs.email)
    session.add(demande)
    session.commit()
    session.refresh(demande)
    
    for n in item.details:
        natures.append(n.nature)
    
    resultats=(
        session.query(Stock)
        .with_entities(Stock.nature,Stock.quantite_disponible)
        .filter(Stock.nature.in_(natures))
        .order_by(Stock.quantite_disponible.desc())
        .all()
    )    
  
    i= 0
    for d in item.details: 
                      
        detail= Demande_Detail(demande_id= demande.id,                                  
                              nature= resultats[i][0],
                              quantite_demandee= d.quantite,
                              quantite_disponible= resultats[i][1]
                              )
      
        session.add(detail)
        session.commit()
        i+=1
        
        session.refresh(detail)
        
        # notification     
        
    return {"demandeur":demande.demandeur, "total demande":len(item.details),
            "details":item.details}



@router.post("/{demande_id}/valider")
def valider_demande(demande_id: int,
                    payload: Demande_validee,
                    session: Session= Depends(get_session)):
   
    natures= []
    demande= session.get(Demande, demande_id)
    if not demande:
        raise HTTPException(404, "Demande introuvable")
    statut_global= "validee"
    
    for v in payload.validations:
            detail = session.get(Demande_Detail, v.detail_id) 
                   
            if not detail or detail.demande_id != demande.id:
                raise HTTPException(404, f"Detail {v.detail_id} introuvable")
            stock= session.query(Stock).filter(Stock.nature==detail.nature).first()
            if not stock:
                raise HTTPException(400, f"Aucun stock trouve pour detail {v.detail_id}")
            
            # Verifications
            
            if v.quantite_validee > detail.quantite_demandee:
                raise HTTPException(400, f"Quantité validée dépasse la quantité démandée ({detail.quantite_demandee})")
            
            if v.quantite_validee > stock.quantite_disponible:
                raise HTTPException(400, f"Quantité validée dépasse le stock disponible ({stock.quantite_disponible})")
                 
            # Mide a jour du stock
            natures.append(detail.nature)
            resultats= (
                session.query(Stock)
                .with_entities(Stock.quantite_disponible)
                .filter(Stock.nature.in_(natures))
            )
            detail.quantite_disponible= resultats[0][0]                
                
            detail.quantite_validee = v.quantite_validee
            
            stock.quantite_disponible -= v.quantite_validee           
           
            if stock.quantite_disponible == 0:
                stock.statut= "epuise"
            # Création de la ligne de l'historique  de validation
            
            validation= Validation(demande_detail_id= detail.did,
                                       nature= stock.nature,
                                       quantite_validee= v.quantite_validee,
                                       valide_par= v.valide_par)
                 
            if v.quantite_validee < detail.quantite_demandee:                
                statut_global= "partiellement_validee"
                demande.statut= statut_global
                session.add(demande)
                session.commit()
                newDemande = Demande(demandeur=demande.demandeur,
                                     demandeur_email= demande.demandeur_email)
                
                if newDemande:
                    session.add(newDemande)
                    session.commit()
                    session.refresh(newDemande)                    
                    newDetail= Demande_Detail(demande_id= newDemande.id,
                                          nature= detail.nature,
                                          quantite_demandee= detail.quantite_demandee - v.quantite_validee,
                                          quantite_disponible= resultats[0][0]
                                          )
                               
                    session.add(newDetail)
                    session.commit()
            
            demande.statut= statut_global
            detail.statut= statut_global
            session.add(detail)
            session.commit()
            session.add(stock)
            session.commit()
            session.add(validation)
            session.commit()
                
            # notification
      
    return {"message": f"Demande de {demande.demandeur} de {detail.quantite_demandee} carnets validée avec statut ({statut_global})"}        


@router.patch("/{demande_id}/distribuer")
def distribuer(demande_id: int,
               series: SerieUpdate,                            
               session: Session= Depends(get_session)):    
   
    dmdDetails= session.exec(
        select(Demande_Detail)
        .where(Demande_Detail.demande_id== demande_id)
        ).first()
    
    dist= Distribution(
      demande_id= demande_id,
      quantite= dmdDetails.quantite_validee,
      distribue_par="Comptabilité",
      
    )
    
    carnetDetails= session.exec(
        select(Details_Carnets)
        .where(and_(
        Details_Carnets.nature== series.nature, 
        Details_Carnets.series== series.series)
    )).first()
    
    if not carnetDetails:
        raise HTTPException(404, "Series non trouvees")
    
    session.add(dist)
    session.commit()
    session.refresh(dist)
        
    carnetDetails.demande_id= demande_id    
    carnetDetails.statut= StatutValidation.distribuee         
    carnetDetails.distribution_id= dist.id
    carnetDetails.date_epuise= date.today()
    
    session.add(carnetDetails)
    session.commit()
    session.refresh(carnetDetails)
    debut,fin = series.series.split("-")
  
    
    return {"message": "Distribution effectuée"}


@router.put("/{id}/rejeter")
def rejeter_demande(id:int,session: Session= Depends(get_session)):    
    demande_detail= session.exec(select(Demande_Detail)
                                 .filter(
                                     and_(Demande_Detail.demande_id== id, Demande_Detail.statut== StatutValidation.en_attente)
                                 )
                                 ).first()

    demande= session.exec(select(Demande)
                                 .filter(Demande.id== id)).first()
    if not demande:        
        raise HTTPException(status_code=404, detail="Demande introuvable ou déjà traitée")
    
    
    demande.statut= StatutValidation.rejetee
    demande_detail.statut= StatutValidation.rejetee
    
    session.add(demande_detail)
    session.commit()
    session.refresh(demande_detail)
    session.add(demande)
    session.commit()
    session.refresh(demande)
    
    return {"message": "Demande rejetée !"}



@router.get("/demandes-idvalides")
def get_id_valides(session: Session= Depends(get_session)):
    slmt= (
        select(Demande_Detail)
                        .order_by(Demande_Detail.did)
                        .where(
                            or_(
                                Demande_Detail.statut== StatutValidation.validee,
                                Demande_Detail.statut== StatutValidation.partiellement_validee
                            )
                        )                       
                    )
    results= session.exec(slmt).all()
    return  [{
            "demande_id": i.demande_id,
            "details_id": i.did,
            "nature": i.nature,
            "quantite_validee": i.quantite_validee    
                        
            } for i in results]   
