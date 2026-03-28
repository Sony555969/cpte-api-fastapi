from typing import List
from fastapi import FastAPI,Depends,HTTPException, WebSocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.stock_routes import router as Stock_router
from app.api.consulter_routes import router as Consulter_router
from app.api.demandes_routes import router as Demande_router
from app.api.distribution_routes import router as Distribution_router
from app.api.epuiser_routes import router as Epuiser_router
from app.core.db import init_db
from app.api.auth_routes import router as auth_router
from app.api.checking_routes import router_qr,router_verifier
from fastapi.staticfiles import StaticFiles
from app.api.pdf_routes import router as pdf_router


@asynccontextmanager
async def lifespan(app:FastAPI):
    
    #code execute au demmarrage
    
    print("Application en cours de demarrage...")
    init_db()
    yield
    
    #code execute a l'arret
    
    print("Application en cours d'arret...")


app = FastAPI(lifespan=lifespan,title="GESTION DES IMPRIMES DE VALEUR", version="1.0.0")

# Monter le dossier externe 
# Attention: sur Windows, utilise un chemin absolu valide 

app.mount("/qrcodes", StaticFiles(directory="C:/qrcodes"), name="qrcodes")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre plus tard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(Stock_router)
app.include_router(Consulter_router)
app.include_router(Demande_router)
app.include_router(Distribution_router)
app.include_router(Epuiser_router)
app.include_router(auth_router)
app.include_router(router_qr)
app.include_router(router_verifier)
app.include_router(pdf_router)


clients=[]



@app.get("/")
def read_root():
    return {"message": "Bienvenu à la Direction des Recettes Non Fiscales "}





  