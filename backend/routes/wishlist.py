from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from backend.db.connection import get_db
from backend.db.models import Wishlist

router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"]
)


class WishlistCreate(BaseModel):
    user_id: str
    event_id: Optional[str] = None
    trek_id: Optional[str] = None
    offroad_id: Optional[str] = None
    destination_id: Optional[str] = None
    notes: Optional[str] = None


@router.get("/{user_id}")
def get_wishlist(user_id: str, db: Session = Depends(get_db)):
    items = db.query(Wishlist).filter(
        Wishlist.user_id == user_id
    ).all()

    return {
        "total": len(items),
        "wishlist": [
            {
                "id": str(w.id),
                "user_id": str(w.user_id),
                "event_id": str(w.event_id) if w.event_id else None,
                "trek_id": str(w.trek_id) if w.trek_id else None,
                "offroad_id": str(w.offroad_id) if w.offroad_id else None,
                "destination_id": str(w.destination_id) if w.destination_id else None,
                "notes": w.notes,
                "created_at": str(w.created_at),
            }
            for w in items
        ]
    }


@router.post("/")
def add_to_wishlist(item: WishlistCreate, db: Session = Depends(get_db)):
    wishlist_item = Wishlist(
        user_id=item.user_id,
        event_id=item.event_id,
        trek_id=item.trek_id,
        offroad_id=item.offroad_id,
        destination_id=item.destination_id,
        notes=item.notes
    )
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)

    return {
        "message": "Added to wishlist ✅",
        "id": str(wishlist_item.id)
    }


@router.delete("/{wishlist_id}")
def remove_from_wishlist(wishlist_id: str, db: Session = Depends(get_db)):
    item = db.query(Wishlist).filter(Wishlist.id == wishlist_id).first()

    if not item:
        return {"error": "Item not found"}

    db.delete(item)
    db.commit()

    return {"message": "Removed from wishlist ✅"}