from app.core.db import get_session
from sqlmodel import Session,select
from fastapi import APIRouter, Depends, HTTPException,Query
from app.models.demande import Demande
from app.models.demande_detail import Demande_Detail
from app.models.stock import Stock
from app.models.enums import StatutValidation
from sqlalchemy import and_, desc, join, or_,func
from app.models.details_carnets import Details_Carnets
from app.models.service_demandeur import Service_demandeur
from datetime import date
from sqlalchemy import func
from app.schemas.epuisesUpdate import RapportEpuises
from app.schemas.distribution_update import vueDistribuee
from typing import List
from sqlalchemy import text



router = APIRouter(prefix="/consulter", tags=["consulter"])


@router.get("/demandes/effectuees")
def get_demandes_effectuees(session: Session= Depends(get_session)):
    demandes_effectuees = (select(Demande.id,Demande.demandeur,Demande_Detail.nature,Demande_Detail.quantite_demandee,Demande_Detail.statut,Demande.date_demande)).join(
        Demande, Demande_Detail.demande_id==Demande.id)
    results=session.execute(demandes_effectuees).all()   
    
    return [{
            "DEMANDE ": i.id,
            "DEMANDEUR ": i.demandeur,            
            "NATURE ": i.nature,
            "QUANTITE DEMANDEE": i.quantite_demandee,            
            "DATE DE DEMANDE ": i.date_demande,
            "STATUT ": i.statut                        
            } for i in results]  
    

@router.get("/demandes/attente")
def get_demandes_en_attente(session: Session = Depends(get_session)):
    # Requête principale
    stmt = (
        select(
            Demande.id,
            Demande.demandeur,
            Demande.demandeur_email,
            Demande.date_demande,
            Demande_Detail.did,
            Demande_Detail.demande_id,
            Demande_Detail.nature,
            Demande_Detail.quantite_demandee,
            Stock.quantite_disponible,
        )
        .join(Demande_Detail, Demande.id == Demande_Detail.demande_id)
        .join(Stock, Demande_Detail.nature == Stock.nature)
        .where(Demande_Detail.statut == StatutValidation.en_attente)
        .order_by(Demande_Detail.demande_id)
    )
    en_attentes = session.exec(stmt).all()

    # Comptage des carnets distribués (groupé par demande_id)
    distribues_stmt = (
        select(
            Details_Carnets.demande_id,
            func.count(Details_Carnets.id)
        )
        .where(Details_Carnets.statut == "distribuee")
        .group_by(Details_Carnets.demande_id)
    )
    counts = dict(session.exec(distribues_stmt).all())

    # Pré-calcul des non_epuise groupés
    non_epuise_stmt = text("""
        SELECT demandeur, nature, COUNT(*) as total
        FROM vuedistribuee
        GROUP BY demandeur, nature
    """)
    non_epuise_results = session.execute(non_epuise_stmt).all()
    non_epuise_map = {
        (row.demandeur, row.nature): row.total
        for row in non_epuise_results
    }

    # Construction du résultat
    results = []
    for d in en_attentes:
        results.append({
            "id": d.id,
            "demandeur": d.demandeur,
            "email": d.demandeur_email,
            "date_demande": d.date_demande,
            "did": d.did,
            "nature": d.nature,
            "quantite_demandee": d.quantite_demandee,
            "quantite_disponible": d.quantite_disponible,
            "non_epuise": non_epuise_map.get((d.demandeur, d.nature), 0),
            "deja_distribue": counts.get(d.demande_id, 0),
        })
    return results

    
@router.get("/stock")
def get_stock_disponible(session: Session= Depends(get_session)):
    stock_disponible = (select(Stock.nature,Stock.quantite_disponible)).where(Stock.statut==StatutValidation.disponible)
    results=session.execute(stock_disponible).all()   
      
    return [{
            "nature": i.nature,
            "quantite_disponible" : i.quantite_disponible                        
            } for i in results]
    


@router.get("/demandes/validees")
def get_quantite_validee(session: Session= Depends(get_session)):
    quantite_validee = (select(Demande.id,Demande_Detail.did,Demande.demandeur,Demande.demandeur_email,Demande_Detail.nature,Demande_Detail.quantite_validee,Demande_Detail.quantite_disponible)).join(
        Demande, Demande_Detail.demande_id==Demande.id).order_by(Demande_Detail.demande_id).where(or_(Demande_Detail.statut== StatutValidation.validee, Demande_Detail.statut==StatutValidation.partiellement_validee))
    results=session.exec(quantite_validee).all()   

    return [{
            "demande_id": i.id,
            "detail_id":i.did,
            "demandeur": i.demandeur,
            "demandeur_email": i.demandeur_email,
            "nature": i.nature,
            "quantite_validee" : i.quantite_validee,
            "quantite_disponible": i.quantite_disponible
                        
            } for i in results]    
    

@router.get("/carnets/distribues")
def get_carnets_distribues(session: Session= Depends(get_session)):
    
    carnets = (select(Demande.demandeur,Demande.date_demande, Details_Carnets.nature,Details_Carnets.series)                      
                      .join(Demande, Details_Carnets.demande_id== Demande.id)
                      .order_by(Demande.demandeur)).where(Details_Carnets.statut== StatutValidation.distribuee)
    
    results=session.exec(carnets).all()   
    
    return [{
            "demandeur": i.demandeur,
            "date_demande": i.date_demande,        
            "nature": i.nature,
            "series": i.series
            } for i in results]   
    

@router.get("/types-iv")
def get_types_iv(session: Session= Depends(get_session)):
    
    return session.exec(select(Stock.nature)
                        .order_by(Stock.nature)
                        ).all()
    
@router.get("/demandeurs")
def get_types_iv(session: Session= Depends(get_session)):
    results=  session.exec(select(Service_demandeur.demandeur, Service_demandeur.email)
                        .order_by(Service_demandeur.demandeur)
                        ).all()    
    return [{
            "demandeur": i.demandeur,
            "email": i.email      
                                    
            } for i in results]  
    

@router.get("/carnet/{series}")
def get_stock_disponible(series:str,session: Session= Depends(get_session)):
    carnet_cherche = (select(Details_Carnets.series,Details_Carnets.nature,Details_Carnets.statut)).where(
        and_(Details_Carnets.series==series, Details_Carnets.statut== StatutValidation.disponible )) 
    results= session.exec(carnet_cherche)
    
    r= session.get(Details_Carnets,series)   
   
    return [{
        "series":i.series,
        "nature": i.nature,
        "statut": i.statut
    }for i in results]
  
  
@router.get("/series/{nature}/{quantite}")
def get_quantite_validee(
                        nature:str,
                        quantite: int, 
                         session: Session= Depends(get_session)):
    series_natures = (select(Details_Carnets.series,Details_Carnets.nature)                      
                      .limit(quantite)
                      .order_by(Details_Carnets.series)).where(and_(Details_Carnets.nature==nature, Details_Carnets.statut== StatutValidation.disponible))
    
    results=session.exec(series_natures).all()   
    
    return [{
            "series": i.series,
            "nature": i.nature        
                        
            } for i in results]   
    


@router.get("/stock/disponible")
def get_stock_disponibles(session: Session= Depends(get_session)):                                       
    
    disponibles = (
        select(Stock.nature,
               func.sum(Stock.quantite_disponible).label("quantite"))
        ).where(Stock.statut== StatutValidation.disponible).group_by(Stock.nature).order_by(Stock.nature)
         
    results=session.exec(disponibles).all()   
    
    return [{
            "nature": i.nature,
            "quantite": i.quantite        
      
            } for i in results]    



    
@router.get("/series/{service}")
def get_series_distribuees(
                        service:str,                         
                         session: Session= Depends(get_session)):
    
    series_natures = (select(Details_Carnets.series,Details_Carnets.nature,Details_Carnets.statut,Demande.id,Demande.demandeur)                      
                      .join(Demande, Details_Carnets.demande_id== Demande.id)
                      .order_by(Details_Carnets.series)).where(and_(Demande.demandeur==service, Details_Carnets.statut== StatutValidation.distribuee))
    
    results=session.exec(series_natures).all()   
    
    return [{
            "series": i.series,
            "nature": i.nature,        
            "id": i.id
            } for i in results] 
    

@router.get("/{service}/distribuees")
def get_quantite_validee(service:str,session: Session= Depends(get_session)):
    quantite_distribuee = (select(Demande.id,Demande.demandeur,Demande.demandeur_email,Demande.date_demande,Demande_Detail.nature,Demande_Detail.quantite_validee)).join(
        Demande, Demande_Detail.demande_id==Demande.id).where(
            and_(
                    Demande_Detail.statut== StatutValidation.distribuee, 
                    Demande.demandeur== service  
            ))
    results=session.exec(quantite_distribuee).all()   
    
    return [{
            "id": i.id,
            "demandeur": i.demandeur,
            "demandeur_email": i.demandeur_email,
            "nature": i.nature,
            "quantite_validee" : i.quantite_validee,
            "date_demande": i.date_demande
                        
            } for i in results]  
    

      
@router.get("/natures")
def get_natures(session: Session = Depends(get_session)):

    natures = (
        session.query(Details_Carnets.nature)
        .distinct()
        .all()
    )

    return [n[0] for n in natures]




@router.get("/rapport-epuises")
def rapport_epuises(
    date_debut: date = Query(..., description="Date début AAAA-MM-JJ"),
    date_fin: date = Query(..., description="Date fin AAAA-MM-JJ"),
    session: Session = Depends(get_session)
):
    """
    Retourne pour chaque nature le nombre de carnets épuisés
    entre date_debut et date_fin.
    Même si le nombre est 0, la nature apparaît.
    """

    # 1️⃣ Récupérer toutes les natures distinctes
    toutes_natures: List[str] = [n[0] for n in session.query(Demande_Detail.nature).distinct().all()]

    # 2️⃣ Compter les épuisés par nature
    results = (
        session.query(
           Details_Carnets.nature,
    func.count(Details_Carnets.id).label("nombre_epuises")
        )
       
        .filter(
            Details_Carnets.statut == "epuise",
            Details_Carnets.date_epuise.between(date_debut, date_fin)
        )
        .group_by(Details_Carnets.nature)
        .all()
    )

    # 3️⃣ Transformer en dict {nature: nombre}
    counts_dict = {r.nature: r.nombre_epuises for r in results}

    # 4️⃣ Créer la liste finale avec toutes les natures
    final_list = [{"nature": n, "nombre_epuises": counts_dict.get(n, 0)} for n in toutes_natures]

    return final_list        


@router.get("/totalDistribues")
def get_total_distribue( 
                        date_debut: date = Query(..., description="Date début AAAA-MM-JJ"),
                        date_fin: date = Query(..., description="Date fin AAAA-MM-JJ"),
                        session: Session = Depends(get_session)):
    result = (
    session.query(
        func.count(Details_Carnets.id).label("nombre_epuises")
    )
    .filter(
        Details_Carnets.statut == "distribuee",
        Details_Carnets.date_epuise.between(date_debut, date_fin)
    )
    .scalar()
)
    
    return {"Total":result}


@router.get("/totalDisponibles")
def get_total_disponible( 
                      
                        session: Session = Depends(get_session)):
    result = (
    session.query(
        func.count(Details_Carnets.id).label("nombre_disponibles")
    )
    .filter(
        Details_Carnets.statut == "disponible"
        
    )
    .scalar()
)
    print("---------------",result)
    return {"Total":result}




#@router.get("/totalNonepuise")
def get_total_disponible_bydemandeur(
    demandeur: str,
    nature: str,
    session: Session
):
    stmt = text("""
        SELECT COUNT(*) 
        FROM vuedistribuee 
        WHERE demandeur LIKE :demandeur 
          AND nature LIKE :nature
    """)
    result = session.execute(
        stmt, 
        {"demandeur": demandeur, "nature": nature}
    ).scalar()
    return result