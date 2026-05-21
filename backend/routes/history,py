from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from backend.db.connection import get_db
from backend.db.models import TravelHistory

router = APIRouter(
    prefix="/history",
    tags=["Travel History"]
)


class HistoryCreate(BaseModel):
    user_id: str
    event_id: Optional[str] = None
    trek_id: Optional[str] = None
    offroad_id: Optional[str] = None
    destination_id: Optional[str] = None
    visited_on: str
    rating: Optional[int] = None
    notes: Optional[str] = None
    personal_tip: Optional[str] = None


class HistoryUpdate(BaseModel):
    rating: Optional[int] = None
    notes: Optional[str] = None
    personal_tip: Optional[str] = None


@router.get("/{user_id}")
def get_history(user_id: str, db: Session = Depends(get_db)):
    items = db.query(TravelHistory).filter(
        TravelHistory.user_id == user_id
    ).order_by(TravelHistory.visited_on.desc()).all()

    return {
        "total": len(items),
        "history": [
            {
                "id": str(h.id),
                "user_id": str(h.user_id),
                "event_id": str(h.event_id) if h.event_id else None,
                "trek_id": str(h.trek_id) if h.trek_id else None,
                "offroad_id": str(h.offroad_id) if h.offroad_id else None,
                "destination_id": str(h.destination_id) if h.destination_id else None,
                "visited_on": str(h.visited_on),
                "rating": h.rating,
                "notes": h.notes,
                "personal_tip": h.personal_tip,
                "created_at": str(h.created_at),
            }
            for h in items
        ]
    }


@router.post("/")
def add_to_history(item: HistoryCreate, db: Session = Depends(get_db)):
    from datetime import date
    history_item = TravelHistory(
        user_id=item.user_id,
        event_id=item.event_id,
        trek_id=item.trek_id,
        offroad_id=item.offroad_id,
        destination_id=item.destination_id,
        visited_on=date.fromisoformat(item.visited_on),
        rating=item.rating,
        notes=item.notes,
        personal_tip=item.personal_tip
    )
    db.add(history_item)
    db.commit()
    db.refresh(history_item)

    return {
        "message": "Trip logged successfully ✅",
        "id": str(history_item.id)
    }


@router.patch("/{history_id}")
def update_history(
    history_id: str,
    update: HistoryUpdate,
    db: Session = Depends(get_db)
):
    item = db.query(TravelHistory).filter(
        TravelHistory.id == history_id
    ).first()

    if not item:
        return {"error": "History item not found"}

    if update.rating is not None:
        item.rating = update.rating
    if update.notes is not None:
        item.notes = update.notes
    if update.personal_tip is not None:
        item.personal_tip = update.personal_tip

    db.commit()
    db.refresh(item)

    return {"message": "Updated successfully ✅"}


@router.delete("/{history_id}")
def delete_history(history_id: str, db: Session = Depends(get_db)):
    item = db.query(TravelHistory).filter(
        TravelHistory.id == history_id
    ).first()

    if not item:
        return {"error": "History item not found"}

    db.delete(item)
    db.commit()

    return {"message": "Deleted successfully ✅"}