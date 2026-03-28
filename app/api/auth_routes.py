# app/api/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token,JWT_SECRET,JWT_ALG
from app.core.db import get_session
from pydantic import BaseModel
from app.core.deps import require_roles,oauth2_scheme
from jose import JWTError, jwt
import bcrypt

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel): 
    email: str 
    password: str 
    role: UserRole = UserRole.AGENT

class LoginRequest(BaseModel): 
    email: str 
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    
@router.post("/register", response_model=UserResponse)
def register(data: RegisterRequest, 
             current_user= Depends(require_roles(UserRole.ADMIN)),
             session: Session = Depends(get_session)):
    
    email = data.email.lower().strip()
    if session.exec(select(User).where(User.email == data.email)).first():
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
        )

    
    u = User(email= email, 
             password_hash=hash_password(data.password),
             role=data.role)
    
    try:
        session.add(u); 
        session.commit(); 
        session.refresh(u)
    
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé"
        )

    return {"id": u.id, "email": u.email, "role": u.role}

@router.post("/login")
def login(data: LoginRequest, session: Session = Depends(get_session)):
   
    u = session.exec(select(User).where(User.email == data.email)).first()
    if not u or not verify_password(data.password, u.password_hash) or not u.is_active:
        raise HTTPException(401, "Identifiants invalides")
    sub = {"id": u.id, "role": u.role}
    # Créer le token JWT avec l'ID et le rôle 
    access_token = create_access_token(user_id=u.id, role=u.role, email= u.email) 
    refresh_token = create_refresh_token(user_id=u.id, role=u.role)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }

@router.post("/refresh")
def refresh(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Token invalide")
        sub = payload["sub"]
        return {"access_token": create_access_token(sub), "token_type": "Bearer"}
    except Exception:
        raise HTTPException(401, "Refresh token expiré ou invalide")

@router.get("/me") 
def read_users_me(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)): 
    try: 
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG]) 
        #user_id: str = payload.get("sub") 
        user_id = int(payload.get("sub"))

        if user_id is None: 
            raise HTTPException(status_code=401, detail="Token invalide") 
    except JWTError: 
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    
    user = session.exec(select(User).where(User.id == int(user_id))).first() 
    if user is None: 
        raise HTTPException(status_code=404, detail="Utilisateur introuvable") 
    # ⚡ Retourne le profil complet 
    return { 
            "id": user.id, 
            "email": user.email, 
            "role": user.role, 
            "is_active": user.is_active 
            }



# @router.post("/admin")
# def create_admin(session: Session = Depends(get_session)):
#     email="fiston@test.com"
#     password="222222"
#     role="supervisor"
    
    
#     hashed_password= bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
#     statement= select(User).where(User.email == email)
#     existing_user= session.exec(statement).first()
        
#     if existing_user:
#             print("user existe")
#             return
        
#     admin= User(email=email, password_hash=hashed_password, role=role)
#     session.add(admin)
#     session.commit()
#     print("compte added")