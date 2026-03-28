from fastapi import APIRouter, Depends, HTTPException
from app.core.db import get_session
from app.core.utils import generer_series,insert_interval
from app.models.stock_carnet import Stock_Carnet
from app.models.details_carnets import Details_Carnets
from app.models.stock import Stock
from sqlmodel import Session




router = APIRouter(prefix="/stock", tags=["stock"])

@router.post("")
def ajouter_carnet(stock: Stock_Carnet, session: Session= Depends(get_session)):
    carnets= add_details_carnets(stock,int(stock.numero_serie_debut),int(stock.numero_serie_fin),int(stock.taille_carnet))
   
    for carnet in carnets:
        session.add(carnet)   
        session.commit()
        
            
    stock.quantite_disponible= len(carnets)
    session.add(stock)
    session.commit()
    session.refresh(stock)
    stock_disponinle= session.query(Stock).filter(Stock.nature==stock.nature).first()
    
    if not stock_disponinle:
        raise HTTPException(404, "Taxe invalide")
    
    stock_disponinle.quantite_disponible += stock.quantite_disponible
    stock_disponinle.stock_carnet_id= stock.id
    stock_disponinle.statut="disponible"
    session.add(stock_disponinle)
    session.commit()   
    return {"message": len(carnets)}
  

def add_details_carnets(stock: Stock_Carnet,begin:int,end:int,taille_carnet: int):
    
    carnets = []  
    for s in generer_series(debut=begin,fin=end,taille_carnet= taille_carnet): 
        
        details = Details_Carnets(
        stock_id=stock.id,
        series= s, 
        nature= stock.nature,
        statut= stock.statut           
        )
       
        carnets.append(details) 
    
    return carnets


    