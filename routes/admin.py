import os
import threading
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, Game
from fetch_and_store_private import fetch_and_store_private
from fetch_and_store_tags import update_tags_logic
from similar_games import update_similar_games
from auth import require_role,hash_password
from fetch_and_store_quick import fetch_and_store_quick
from utils.errors import create_error

# BGG-Credentials aus Umgebungsvariablen
bgg_username = os.getenv("BGG_USERNAME")
bgg_password = os.getenv("BGG_PASSWORD")
default_password = os.getenv("DEFAULT_USER_PASSWORD")

router = APIRouter()

# Globaler Lock, um parallele Imports zu verhindern
import_lock = threading.Lock()

@router.post("/import_collection_quick")
def fetch_private_collection_quick(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("helper"))
):
    # Versuche, den Lock nicht-blockierend zu erwerben
    if not import_lock.acquire(blocking=False):
        create_error(
            status_code=409,
            error_code="IMPORT_IN_PROGRESS",
        )
    try:
        result = fetch_and_store_quick(bgg_username, fastMode=True)
        return result  
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", detailed_message=str(e))
    finally:
        import_lock.release()


@router.post("/import_collection_complete")
def fetch_complete_collection(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("admin"))
):
    if not import_lock.acquire(blocking=False):
        create_error(
            status_code=409,
            error_code="IMPORT_IN_PROGRESS",
        )
    try:
        result = fetch_and_store_private(bgg_username, bgg_password)
        changes = update_tags_logic(only_missing_tags=True)
        similarities = update_similar_games(max_similar_games=10)
        return {"result": result, "changes": changes, "similarities": similarities}
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", detailed_message=str(e))
    finally:
        import_lock.release()


@router.post("/import_collection_only") 
def fetch_private_collection(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("admin"))
):
    if not import_lock.acquire(blocking=False):
        create_error(
            status_code=409,
            error_code="IMPORT_IN_PROGRESS",
        )
    try:
        result = fetch_and_store_private(bgg_username, bgg_password)
        return result  
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", detailed_message=str(e))
    finally:
        import_lock.release()


@router.post("/import_tags_only")
def fetch_tags_endpoint(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("admin"))
):
    """
    Endpoint zum Abrufen und Speichern von Tags aus externen Quellen.
    """
    if not import_lock.acquire(blocking=False):
        create_error(
            status_code=409,
            error_code="IMPORT_IN_PROGRESS",
        )
    try:
        changes = update_tags_logic(only_missing_tags=False)
        return {"message": "Tags fetched and saved successfully.", "changes": changes}
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", detailed_message=str(e))
    finally:
        import_lock.release()


@router.post("/update_similar_games_only")
def update_similar_games_endpoint(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("admin"))
):
    """
    Endpoint zum Aktualisieren ähnlicher Spiele basierend auf den Tags.
    """
    if not import_lock.acquire(blocking=False):
        create_error(
            status_code=409,
            error_code="IMPORT_IN_PROGRESS",
        )
    try:
        similarities = update_similar_games(max_similar_games=10)
        return {"message": "Similar games updated successfully.", "similarities": similarities}
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", detailed_message=str(e))
    finally:
        import_lock.release()

@router.put("/admin/reset_borrow_count")
def reset_borrow_count_for_all_games(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    updated_rows = db.query(Game).update({Game.borrow_count: 0}, synchronize_session=False)
    db.commit()
    return {
        "message": "Borrow count for all games has been reset.",
        "updated_rows": updated_rows
    }

@router.put("/admin/reset_available")
def reset_available_for_all_games(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    updated_rows = db.query(Game).update({Game.available: Game.quantity}, synchronize_session=False)
    db.commit()
    return {
        "message": "For all games, 'available' has been reset to match 'quantity'.",
        "updated_rows": updated_rows
    }

@router.put("/admin/reset-password")
def reset_user_password(
    username_or_email: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    user = db.query(User).filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user:
        create_error(status_code=404, error_code="INTERNAL_ERROR")

    user.hashed_password = hash_password(default_password)
    user.force_password_change = True

    db.commit()
    db.refresh(user)

    return {"message": f"Passwort für {user.username} zurückgesetzt:, Nutzer sollte neues Passwort setzen."}