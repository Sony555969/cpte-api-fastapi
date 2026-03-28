from fastapi_mail import ConnectionConfig
import os
from dotenv import load_dotenv


load_dotenv() # charge le fichier .env

def get_env_var(name: str) -> str: 
    value = os.getenv(name) 
    if not value: 
        raise ValueError(f"Variable d'environnement {name} manquante ou vide") 
    return value

mail_config= ConnectionConfig(
    MAIL_USERNAME= get_env_var("MAIL_USERNAME"), 
    MAIL_PASSWORD= get_env_var("MAIL_PASSWORD"), 
    MAIL_FROM= get_env_var("MAIL_FROM"), 
    MAIL_PORT= int(get_env_var("MAIL_PORT")),
    MAIL_SERVER= get_env_var("MAIL_SERVER"), 
    MAIL_STARTTLS= get_env_var("MAIL_STARTTLS") == "True", 
    MAIL_SSL_TLS= get_env_var("MAIL_SSL_TLS") == "True", 
    USE_CREDENTIALS= get_env_var("USE_CREDENTIALS") == "True", 
    VALIDATE_CERTS= get_env_var("VALIDATE_CERTS") == "True"
)