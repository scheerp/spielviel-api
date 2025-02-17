from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from fetch_and_store_private import fetch_and_store_private
from fetch_and_store_tags import update_tags_logic
from similar_games import update_similar_games
from auth import require_role
from fetch_and_store_quick import fetch_and_store_quick
from utils.errors import create_error
import os


bgg_username = os.getenv("BGG_USERNAME")
bgg_password = os.getenv("BGG_PASSWORD")

router = APIRouter()

@router.post("/import_collection_quick")
def fetch_private_collection_quick(db: Session = Depends(get_db), current_user: User = Depends(require_role("helper"))):
    try:
        result = fetch_and_store_quick(bgg_username, fastMode=True)
        return result  
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", details=str(e))
    

@router.post("/import_collection_complete")
def fetch_complete_collection(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    try:
        result = fetch_and_store_private(bgg_username, bgg_password)
        changes = update_tags_logic(only_missing_tags=True)
        similarities = update_similar_games(max_similar_games=10)
        return {"result": result, "changes": changes, "similarities": similarities}
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", details=str(e))
    
    
@router.post("/import_collection_only") 
def fetch_private_collection(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    try:
        result = fetch_and_store_private(bgg_username, bgg_password)
        return result  
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", details=str(e))
    

@router.post("/import_tags_only")
def fetch_tags_endpoint(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    """
    Endpoint to fetch tags from external sources and save them in the database.
    """
    try:
        changes = update_tags_logic(only_missing_tags=False)
        return {"message": "Tags fetched and saved successfully.", "changes": changes}
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", details=str(e))


@router.post("/update_similar_games_only")
def update_similar_games_endpoint(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    """
    Endpoint to find and update similar games based on their tags.
    """
    try:
        similarities = update_similar_games(max_similar_games=10)
        return {"message": "Similar games updated successfully.", "similarities": similarities}
    except Exception as e:
        create_error(status_code=500, error_code="INTERNAL_ERROR", details=str(e))