from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from backend.db.connection import get_db
from backend.db.models import Destination

router = APIRouter(
    prefix="/destinations",
    tags=["Destinations"]
)


@router.get("/")
def get_destinations(
    country: Optional[str] = Query(None),
    month: Optional[int] = Query(None),
    is_offbeat: Optional[bool] = Query(None),
    tags: Optional[str] = Query(None),
    popularity: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Destination)

    # filter by country
    if country:
        query = query.filter(Destination.country.ilike(f"%{country}%"))

    # filter by best month
    if month:
        query = query.filter(
            Destination.best_month_start <= month,
            Destination.best_month_end >= month
        )

    # filter by offbeat
    if is_offbeat is not None:
        query = query.filter(Destination.is_offbeat == is_offbeat)

    # filter by tags
    if tags:
        query = query.filter(
            Destination.tags.any(tags.lower())
        )

    # search
    if q:
        query = query.filter(
            or_(
                Destination.name.ilike(f"%{q}%"),
                Destination.country.ilike(f"%{q}%"),
                Destination.description.ilike(f"%{q}%")
            )
        )

    # sort by popularity
    if popularity == "high":
        query = query.order_by(Destination.popularity_score.desc()) \
            if hasattr(Destination, 'popularity_score') else query
    else:
        query = query.order_by(Destination.created_at.desc())

    destinations = query.all()

    return {
        "total": len(destinations),
        "destinations": [
            {
                "id": str(d.id),
                "name": d.name,
                "country": d.country,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "description": d.description,
                "best_month_start": d.best_month_start,
                "best_month_end": d.best_month_end,
                "image_url": d.image_url,
                "youtube_url": d.youtube_url,
                "is_offbeat": d.is_offbeat,
                "tags": d.tags,
            }
            for d in destinations
        ]
    }


@router.get("/{destination_id}")
def get_destination(destination_id: str, db: Session = Depends(get_db)):
    dest = db.query(Destination).filter(
        Destination.id == destination_id
    ).first()

    if not dest:
        return {"error": "Destination not found"}

    return {
        "id": str(dest.id),
        "name": dest.name,
        "country": dest.country,
        "latitude": dest.latitude,
        "longitude": dest.longitude,
        "description": dest.description,
        "best_month_start": dest.best_month_start,
        "best_month_end": dest.best_month_end,
        "image_url": dest.image_url,
        "youtube_url": dest.youtube_url,
        "is_offbeat": dest.is_offbeat,
        "tags": dest.tags,
    }