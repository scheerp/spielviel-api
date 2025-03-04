import os
import re
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session
from auth import hash_password, create_access_token, verify_password, require_role, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from models import User, RegisterRequest, ChangePasswordRequest
from datetime import timedelta
from utils.errors import create_error

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

required_invite = os.getenv("HELPER_INVITE_CODE")
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+={}\[\]:;'\"<>,.?/\\|-]{6,}$"


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Prüfen, ob es eine E-Mail ist (nach @ suchen)
    is_email = re.match(EMAIL_REGEX, form_data.username)

    # User entweder über Username oder E-Mail finden
    user = db.query(User).filter(
        or_(User.username == form_data.username, User.email == form_data.username)
    ).first()

    # Falls kein User existiert oder Passwort falsch ist
    if not user or not verify_password(form_data.password, user.hashed_password):
        create_error(status_code=status.HTTP_401_UNAUTHORIZED, error_code="NOT_AUTHORIZED")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {
        "id": user.id,
        "sub": user.username,
        "role": user.role
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "id": user.id, "username": user.username}



@router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    # Invite-Code prüfen
    if request.invite_code != required_invite:
        create_error(status_code=status.HTTP_403_FORBIDDEN, error_code="INVALID_INVITE_CODE")

    # E-Mail-Validierung
    if not re.match(EMAIL_REGEX, request.email):
        create_error(status_code=status.HTTP_400_BAD_REQUEST, error_code="INVALID_EMAIL")

    # Passwort-Validierung
    if not re.match(PASSWORD_REGEX, request.password):
        create_error(status_code=status.HTTP_400_BAD_REQUEST, error_code="INVALID_PASSWORD", detailed_message="Passwort muss mindestens 6 Zeichen lang sein, eine Zahl und einen Großbuchstaben enthalten.")

    # Prüfen, ob Nutzername oder E-Mail bereits existieren
    existing_user = db.query(User).filter(User.username == request.username).first()
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_user or existing_email:
        create_error(status_code=status.HTTP_409_CONFLICT, error_code="USER_ALREADY_EXISTS")

    # Passwort hashen und Benutzer anlegen
    hashed_pw = hash_password(request.password)
    user = User(username=request.username, email=request.email, hashed_password=hashed_pw, role="helper")
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User erfolgreich erstellt", "username": user.username}

@router.put("/change-password")
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("guest"))
):
    # Überprüfen, ob das aktuelle Passwort korrekt ist
    if not verify_password(request.current_password, current_user.hashed_password):
        create_error(status_code=status.HTTP_400_BAD_REQUEST, error_code="INVALID_CURRENT_PASSWORD")

    # Neues Passwort hashen
    new_hashed_password = hash_password(request.new_password)

    # Passwort in der Datenbank aktualisieren
    current_user.hashed_password = new_hashed_password
    db.commit()
    db.refresh(current_user)

    return {"message": "Passwort erfolgreich geändert"}
