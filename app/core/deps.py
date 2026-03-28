# app/core/deps.py
from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.core.db import get_session
from typing import List
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt


# 👉 URL du endpoint de login qui génère le token 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/auth/login") 

# Clé secrète et algorithme utilisés pour signer le JWT 
JWT_SECRET = "info@2025@drnoFLU" 
# ⚠️ à mettre dans une variable d'environnement 
ALGORITHM = "HS256"


def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session) ) -> User: 
    try: # Décoder le JWT 
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM]) 
        user_id: int = payload.get("sub") 
        if user_id is None: 
            raise HTTPException( 
                                status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Token invalide", 
                                headers={"WWW-Authenticate": "Bearer"}, 
                                ) 
    except JWTError: 
            raise HTTPException( 
                                status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail="Token invalide ou expiré", 
                                headers={"WWW-Authenticate": "Bearer"}, 
                                )
    user = session.exec(select(User).where(User.id == user_id)).first() 
    if user is None: 
        raise HTTPException( 
                            status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail="Utilisateur introuvable", 
                            headers={"WWW-Authenticate": "Bearer"}, 
                            ) 
    return user

def require_roles(*roles: List[UserRole]): 
    def role_checker(current_user: User = Depends(get_current_user)): 
        if current_user.role not in roles: 
            raise HTTPException( status_code=status.HTTP_403_FORBIDDEN, 
                                detail="Accès refusé : rôle insuffisant" ) 
        return current_user 
    return role_checker
