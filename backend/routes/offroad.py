from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from backend.db.connection import get_db
from backend.db.models import OffroadTrail

router = APIRouter(
    prefix="/offroad",
    tags=["Offroad Trails"]
)


@router.get("/")
def get_offroad_trails(
    country: Optional[str] = Query(None),
    month: Optional[int] = Query(None),
    vehicle_type: Optional[str] = Query(None),
    terrain_type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    road_condition: Optional[str] = Query(None),
    is_offbeat: Optional[bool] = Query(None),
    popularity: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(OffroadTrail)

    # filter by country
    if country:
        query = query.filter(OffroadTrail.country.ilike(f"%{country}%"))

    # filter by best month
    if month:
        query = query.filter(
            OffroadTrail.best_month_start <= month,
            OffroadTrail.best_month_end >= month
        )

    # filter by vehicle type
    if vehicle_type:
        query = query.filter(OffroadTrail.vehicle_type == vehicle_type)

    # filter by terrain
    if terrain_type:
        query = query.filter(OffroadTrail.terrain_type == terrain_type)

    # filter by difficulty
    if difficulty:
        query = query.filter(OffroadTrail.difficulty == difficulty)

    # filter by road condition
    if road_condition:
        query = query.filter(OffroadTrail.road_condition == road_condition)

    # filter by offbeat
    if is_offbeat is not None:
        query = query.filter(OffroadTrail.is_offbeat == is_offbeat)

    # search
    if q:
        query = query.filter(
            or_(
                OffroadTrail.name.ilike(f"%{q}%"),
                OffroadTrail.country.ilike(f"%{q}%"),
                OffroadTrail.description.ilike(f"%{q}%")
            )
        )

    # sort by popularity
    if popularity == "high":
        query = query.order_by(OffroadTrail.popularity_score.desc())
    else:
        query = query.order_by(OffroadTrail.created_at.desc())

    trails = query.all()

    return {
        "total": len(trails),
        "trails": [
            {
                "id": str(t.id),
                "name": t.name,
                "country": t.country,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "vehicle_type": t.vehicle_type,
                "terrain_type": t.terrain_type,
                "difficulty": t.difficulty,
                "road_condition": t.road_condition,
                "best_month_start": t.best_month_start,
                "best_month_end": t.best_month_end,
                "description": t.description,
                "distance_km": t.distance_km,
                "popularity_score": t.popularity_score,
                "image_url": t.image_url,
                "youtube_url": t.youtube_url,
                "is_offbeat": t.is_offbeat,
            }
            for t in trails
        ]
    }


@router.get("/{trail_id}")
def get_offroad_trail(trail_id: str, db: Session = Depends(get_db)):
    trail = db.query(OffroadTrail).filter(OffroadTrail.id == trail_id).first()

    if not trail:
        return {"error": "Trail not found"}

    return {
        "id": str(trail.id),
        "name": trail.name,
        "country": trail.country,
        "latitude": trail.latitude,
        "longitude": trail.longitude,
        "vehicle_type": trail.vehicle_type,
        "terrain_type": trail.terrain_type,
        "difficulty": trail.difficulty,
        "road_condition": trail.road_condition,
        "best_month_start": trail.best_month_start,
        "best_month_end": trail.best_month_end,
        "description": trail.description,
        "distance_km": trail.distance_km,
        "popularity_score": trail.popularity_score,
        "image_url": trail.image_url,
        "youtube_url": trail.youtube_url,
        "is_offbeat": trail.is_offbeat,
    }