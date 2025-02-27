from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import UserGameKnowledge, User, UserGameKnowledgeResponse, UserGameKnowledgeRequest
from auth import require_role

router = APIRouter()

@router.put("/{game_id}/familiarity", response_model=UserGameKnowledgeResponse)
def update_game_familiarity(
    game_id: int,
    request: UserGameKnowledgeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("helper"))
):
    record = db.query(UserGameKnowledge).filter(
        UserGameKnowledge.game_id == game_id,
        UserGameKnowledge.user_id == current_user.id
    ).first()

    if record:
        record.familiarity = request.familiarity
    else:
        record = UserGameKnowledge(
            user_id=current_user.id,
            game_id=game_id,
            familiarity=request.familiarity
        )
        db.add(record)
    
    db.commit()
    db.refresh(record)
    return record
