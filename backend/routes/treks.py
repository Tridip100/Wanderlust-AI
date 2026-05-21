from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from backend.db.connection import get_db
from backend.db.models import Trek

router = APIRouter(
    prefix="/treks",
    tags=["Treks"]
)


@router.get("/")
def get_treks(
    country: Optional[str] = Query(None),
    month: Optional[int] = Query(None),
    difficulty: Optional[str] = Query(None),
    terrain_type: Optional[str] = Query(None),
    is_offbeat: Optional[bool] = Query(None),
    popularity: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Trek)

    # filter by country
    if country:
        query = query.filter(Trek.country.ilike(f"%{country}%"))

    # filter by best month
    if month:
        query = query.filter(
            Trek.best_month_start <= month,
            Trek.best_month_end >= month
        )

    # filter by difficulty
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)

    # filter by terrain
    if terrain_type:
        query = query.filter(Trek.terrain_type == terrain_type)

    # filter by offbeat
    if is_offbeat is not None:
        query = query.filter(Trek.is_offbeat == is_offbeat)

    # search
    if q:
        query = query.filter(
            or_(
                Trek.name.ilike(f"%{q}%"),
                Trek.country.ilike(f"%{q}%"),
                Trek.description.ilike(f"%{q}%")
            )
        )

    # sort by popularity
    if popularity == "high":
        query = query.order_by(Trek.popularity_score.desc())
    else:
        query = query.order_by(Trek.created_at.desc())

    treks = query.all()

    return {
        "total": len(treks),
        "treks": [
            {
                "id": str(t.id),
                "name": t.name,
                "country": t.country,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "difficulty": t.difficulty,
                "best_month_start": t.best_month_start,
                "best_month_end": t.best_month_end,
                "description": t.description,
                "distance_km": t.distance_km,
                "duration_days": t.duration_days,
                "popularity_score": t.popularity_score,
                "image_url": t.image_url,
                "youtube_url": t.youtube_url,
                "terrain_type": t.terrain_type,
                "is_offbeat": t.is_offbeat,
            }
            for t in treks
        ]
    }


@router.get("/{trek_id}")
def get_trek(trek_id: str, db: Session = Depends(get_db)):
    trek = db.query(Trek).filter(Trek.id == trek_id).first()

    if not trek:
        return {"error": "Trek not found"}

    return {
        "id": str(trek.id),
        "name": trek.name,
        "country": trek.country,
        "latitude": trek.latitude,
        "longitude": trek.longitude,
        "difficulty": trek.difficulty,
        "best_month_start": trek.best_month_start,
        "best_month_end": trek.best_month_end,
        "description": trek.description,
        "distance_km": trek.distance_km,
        "duration_days": trek.duration_days,
        "popularity_score": trek.popularity_score,
        "image_url": trek.image_url,
        "youtube_url": trek.youtube_url,
        "terrain_type": trek.terrain_type,
        "is_offbeat": trek.is_offbeat,
    }