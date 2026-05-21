from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from backend.db.connection import get_db
from backend.db.models import UserFeedback

router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"]
)


class FeedbackCreate(BaseModel):
    user_id: str
    type: str
    message: str


@router.post("/")
def submit_feedback(item: FeedbackCreate, db: Session = Depends(get_db)):
    feedback = UserFeedback(
        user_id=item.user_id,
        type=item.type,
        message=item.message
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return {
        "message": "Feedback submitted ✅",
        "id": str(feedback.id)
    }


@router.get("/")
def get_all_feedback(
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(UserFeedback)

    if type:
        query = query.filter(UserFeedback.type == type)

    items = query.order_by(UserFeedback.created_at.desc()).all()

    return {
        "total": len(items),
        "feedback": [
            {
                "id": str(f.id),
                "user_id": str(f.user_id),
                "type": f.type,
                "message": f.message,
                "created_at": str(f.created_at),
            }
            for f in items
        ]
    }