from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract
from typing import Optional
from backend.db.connection import get_db
from backend.db.models import Event, Trek, OffroadTrail

router = APIRouter(
    prefix="/heatmap",
    tags=["Heatmap"]
)


@router.get("/")
def get_heatmap(
    month: Optional[int] = Query(None),
    type: Optional[str] = Query(None),  # events / treks / offroad / all
    db: Session = Depends(get_db)
):
    points = []

    # ── EVENTS ──────────────────────────────────────
    if type in (None, "all", "events"):
        event_query = db.query(Event)
        if month:
            event_query = event_query.filter(
                extract("month", Event.start_date) == month
            )
        events = event_query.all()

        for e in events:
            # heatmap weight formula
            seasonal_score = 1.0
            if month:
                event_month = e.start_date.month if e.start_date else 0
                seasonal_score = 1.0 if event_month == month else 0.5

            weight = (
                e.popularity_score * 0.5 +
                seasonal_score * 0.3 +
                (0.2 if e.is_offbeat else 0.1)
            )

            points.append({
                "lat": e.latitude,
                "lng": e.longitude,
                "weight": round(min(weight, 1.0), 4),
                "label": e.name,
                "type": "event"
            })

    # ── TREKS ────────────────────────────────────────
    if type in (None, "all", "treks"):
        trek_query = db.query(Trek)
        if month:
            trek_query = trek_query.filter(
                Trek.best_month_start <= month,
                Trek.best_month_end >= month
            )
        treks = trek_query.all()

        for t in treks:
            seasonal_score = 1.0
            if month:
                in_season = (
                    t.best_month_start <= month <= t.best_month_end
                )
                seasonal_score = 1.0 if in_season else 0.4

            weight = (
                t.popularity_score * 0.5 +
                seasonal_score * 0.3 +
                (0.2 if t.is_offbeat else 0.1)
            )

            points.append({
                "lat": t.latitude,
                "lng": t.longitude,
                "weight": round(min(weight, 1.0), 4),
                "label": t.name,
                "type": "trek"
            })

    # ── OFFROAD ──────────────────────────────────────
    if type in (None, "all", "offroad"):
        offroad_query = db.query(OffroadTrail)
        if month:
            offroad_query = offroad_query.filter(
                OffroadTrail.best_month_start <= month,
                OffroadTrail.best_month_end >= month
            )
        trails = offroad_query.all()

        for o in trails:
            seasonal_score = 1.0
            if month:
                in_season = (
                    o.best_month_start <= month <= o.best_month_end
                )
                seasonal_score = 1.0 if in_season else 0.4

            weight = (
                o.popularity_score * 0.5 +
                seasonal_score * 0.3 +
                (0.2 if o.is_offbeat else 0.1)
            )

            points.append({
                "lat": o.latitude,
                "lng": o.longitude,
                "weight": round(min(weight, 1.0), 4),
                "label": o.name,
                "type": "offroad"
            })

    return {
        "total": len(points),
        "month": month,
        "points": points
    }