from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional
from backend.db.connection import get_db
from backend.db.models import Event, Trek, OffroadTrail

router = APIRouter(
    prefix="/map",
    tags=["Map"]
)


@router.get("/pins")
def get_map_pins(
    month: Optional[int] = Query(None),
    country: Optional[str] = Query(None),
    type: Optional[str] = Query(None),  # events / treks / offroad / all
    is_offbeat: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    pins = []

    # ── EVENTS ──────────────────────────────────────
    if type in (None, "all", "events"):
        event_query = db.query(Event)

        if month:
            event_query = event_query.filter(
                extract("month", Event.start_date) == month
            )
        if country:
            event_query = event_query.filter(
                Event.country.ilike(f"%{country}%")
            )
        if is_offbeat is not None:
            event_query = event_query.filter(
                Event.is_offbeat == is_offbeat
            )

        for e in event_query.all():
            pins.append({
                "id": str(e.id),
                "name": e.name,
                "lat": e.latitude,
                "lng": e.longitude,
                "type": "event",
                "subtype": e.type,
                "country": e.country,
                "city": e.city,
                "popularity_score": e.popularity_score,
                "is_offbeat": e.is_offbeat,
                "image_url": e.image_url,
                "start_date": str(e.start_date) if e.start_date else None,
                "end_date": str(e.end_date) if e.end_date else None,
            })

    # ── TREKS ────────────────────────────────────────
    if type in (None, "all", "treks"):
        trek_query = db.query(Trek)

        if month:
            trek_query = trek_query.filter(
                Trek.best_month_start <= month,
                Trek.best_month_end >= month
            )
        if country:
            trek_query = trek_query.filter(
                Trek.country.ilike(f"%{country}%")
            )
        if is_offbeat is not None:
            trek_query = trek_query.filter(
                Trek.is_offbeat == is_offbeat
            )

        for t in trek_query.all():
            pins.append({
                "id": str(t.id),
                "name": t.name,
                "lat": t.latitude,
                "lng": t.longitude,
                "type": "trek",
                "subtype": t.terrain_type,
                "country": t.country,
                "difficulty": t.difficulty,
                "popularity_score": t.popularity_score,
                "is_offbeat": t.is_offbeat,
                "image_url": t.image_url,
                "duration_days": t.duration_days,
                "distance_km": t.distance_km,
            })

    # ── OFFROAD ──────────────────────────────────────
    if type in (None, "all", "offroad"):
        offroad_query = db.query(OffroadTrail)

        if month:
            offroad_query = offroad_query.filter(
                OffroadTrail.best_month_start <= month,
                OffroadTrail.best_month_end >= month
            )
        if country:
            offroad_query = offroad_query.filter(
                OffroadTrail.country.ilike(f"%{country}%")
            )
        if is_offbeat is not None:
            offroad_query = offroad_query.filter(
                OffroadTrail.is_offbeat == is_offbeat
            )

        for o in offroad_query.all():
            pins.append({
                "id": str(o.id),
                "name": o.name,
                "lat": o.latitude,
                "lng": o.longitude,
                "type": "offroad",
                "subtype": o.vehicle_type,
                "country": o.country,
                "difficulty": o.difficulty,
                "road_condition": o.road_condition,
                "popularity_score": o.popularity_score,
                "is_offbeat": o.is_offbeat,
                "image_url": o.image_url,
                "distance_km": o.distance_km,
            })

    return {
        "total": len(pins),
        "total_events": len([p for p in pins if p["type"] == "event"]),
        "total_treks": len([p for p in pins if p["type"] == "trek"]),
        "total_offroad": len([p for p in pins if p["type"] == "offroad"]),
        "pins": pins
    }