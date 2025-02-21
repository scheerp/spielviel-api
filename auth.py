from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User
from utils.errors import create_error
from database import get_db
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5760
ROLE_PERMISSIONS = {
    "admin": ["helper", "guest", "admin"],
    "helper": ["helper", "guest"],
    "guest": ["guest"],
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def require_role(required_role: str):
    """Factory-Funktion zur Generierung von Rollen-basierten Dependencies"""
    def role_checker(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        user = get_current_user(token, db)
        if user.role not in ROLE_PERMISSIONS:
            create_error(status_code=403, error_code="NOT_AUTHORIZED")

        if required_role not in ROLE_PERMISSIONS[user.role]:
            create_error(status_code=403, error_code="PERMISSION_DENIED")

        return user  # ✅ Berechtigter User wird zurückgegeben

    return role_checker


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Passwort-Überprüfungsfunktionen
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# JWT-Erstellung
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Funktion zur Authentifizierung
def get_current_user(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    return user
