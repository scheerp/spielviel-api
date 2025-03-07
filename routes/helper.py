from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from database import get_db
from utils.errors import create_error
from collections import defaultdict
from models import UserGameKnowledge, User, GameResponse, UserGameKnowledgeRequest, GameExplainersResponse, Game
from auth import require_role

router = APIRouter()

@router.put("/{game_id}/familiarity", response_model=GameResponse)
def update_game_familiarity(
    game_id: int,
    request: UserGameKnowledgeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("helper"))
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")
    
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
    db.refresh(record)  # Das UserGameKnowledge-Objekt wird aktualisiert

    # Das Spiel-Objekt ebenfalls aktualisieren
    db.refresh(game)

    # Verwende model_validate anstelle von from_orm
    game_response = GameResponse.model_validate(game)

    # Hinzufügen des my_familiarity-Werts zum GameResponse
    game_response.my_familiarity = record.familiarity

    return game_response



@router.get("/{game_id}/explainers", response_model=GameExplainersResponse)
def get_game_explainers(
    game_id: int,
    user_id: int = Query(..., alias="user_id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("helper"))
):
    game = (
        db.query(Game)
        .options(joinedload(Game.user_knowledge).joinedload(UserGameKnowledge.user))
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")

    explainer_groups_dict = defaultdict(list)
    my_familiarity = None

    for uk in game.user_knowledge:
        if uk.familiarity > 1:
            explainer_groups_dict[uk.familiarity].append({
                "id": uk.user.id,
                "username": uk.user.username,
                "familiarity": uk.familiarity
            })
        if uk.user.id == user_id:
            my_familiarity = uk.familiarity

    explainer_groups = [
        {"familiarity": familiarity, "users": users}
        for familiarity, users in sorted(explainer_groups_dict.items(), key=lambda x: x[0], reverse=True)
    ]
    
    return {"my_familiarity": my_familiarity, "explainers": explainer_groups}
