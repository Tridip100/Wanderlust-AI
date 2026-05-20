from fastapi import APIRouter, Depends , Query 
from sqlalchemy.orm import Session
from sqlalchemy import extract, or_
from typing import Optional 
from backend.db.connection import get_db
from backend.db.models import Event

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

@router.get("/")
def get_eventns(
    country : Optional[str] = Query(None),
    month : Optional[int] = Query(None),
    type : Optional[str] = Query(None),
    is_offbeat : Optional[bool] = Query(None),
    popularity : Optional[str] = Query(None),
    search : Optional[str] = Query(None),
    db : Session = Depends(get_db)
):
    query = db.query(Event)

    if country:
        query = query.filter(Event.country.ilike(f"%{country}%"))

    if month:
        query = query.filter(
        extract("month", Event.start_date) == month
        )
    
    if type:
        query = query.filter(Event.type == type)
    
    if search:
        query = query.filter(
            or_(
                Event.name.ilike(f"%{search}%"),
                Event.city.ilike(f"%{search}%"),
                Event.country.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%")
            )
        )

    if popularity == 'high':
        query = query.order_by(Event.popularity_score.desc())
    else:
        query = query.order_by(Event.created_at.desc())

    events = query.all()


    return {
        "total": len(events),
        "events": [
            {
                "id": str(e.id),
                "name": e.name,
                "country": e.country,
                "city": e.city,
                "latitude": e.latitude,
                "longitude": e.longitude,
                "start_date": str(e.start_date),
                "end_date": str(e.end_date),
                "type": e.type,
                "description": e.description,
                "popularity_score": e.popularity_score,
                "image_url": e.image_url,
                "youtube_url": e.youtube_url,
                "is_offbeat": e.is_offbeat,
            }
            for e in events
        ]
    }


@router.get("/{event_id}")
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        return {"error": "Event not found"}

    return {
        "id": str(event.id),
        "name": event.name,
        "country": event.country,
        "city": event.city,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "start_date": str(event.start_date),
        "end_date": str(event.end_date),
        "type": event.type,
        "description": event.description,
        "popularity_score": event.popularity_score,
        "image_url": event.image_url,
        "youtube_url": event.youtube_url,
        "is_offbeat": event.is_offbeat,
    }
            
