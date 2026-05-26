import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
from mistralai.client.sdk import Mistral
from backend.db.connection import SessionLocal
from backend.db.models import Event, Trek, OffroadTrail, Destination
from backend.config import config
from datetime import date

client = Mistral(api_key=config.MISTRAL_API_KEY)


def generate_data(prompt: str) -> list:
    response = client.chat.complete(
        model=config.MISTRAL_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are a travel data expert.
                Return ONLY a valid JSON array.
                No markdown, no backticks, no explanation.
                Just the raw JSON array starting with [ and ending with ]
                Keep descriptions short — max 1 sentence each."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=4000,
    )

    raw = response.choices[0].message.content.strip()

    # clean markdown if present
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    # fix truncated JSON — find last complete object
    if not raw.endswith("]"):
        last_complete = raw.rfind("},")
        if last_complete != -1:
            raw = raw[:last_complete + 1] + "]"
        else:
            raw = raw + "]"

    return json.loads(raw)

VALID_EVENT_TYPES = [
    'festival', 'carnival', 'cultural',
    'fair', 'spiritual', 'food', 'music', 'adventure'
]

TYPE_MAP = {
    'religious': 'spiritual',
    'traditional': 'cultural',
    'celebration': 'festival',
    'parade': 'carnival',
    'ceremony': 'cultural',
    'sport': 'adventure',
    'arts': 'cultural',
    'market': 'fair',
}


def seed_events(db):
    print("🎪 Generating events data...")
    
    prompt = """Generate 30 real world festivals and cultural events as a JSON array.
    Include famous AND hidden/offbeat events from India, Japan, Nepal, Thailand, 
    Europe, Americas, Africa, Southeast Asia.
    
    Each object must have exactly these fields:
    {
        "name": "festival name",
        "country": "country name",
        "city": "city name",
        "latitude": 00.0000,
        "longitude": 00.0000,
        "start_month": 1-12,
        "end_month": 1-12,
        "start_day": 1-28,
        "end_day": 1-28,
        "type": "festival OR carnival OR cultural OR fair OR spiritual OR food OR music OR adventure",
        "description": "2-3 sentences describing this event vividly",
        "popularity_score": 0.0-1.0,
        "is_offbeat": true or false
    }
    
    Make sure coordinates are accurate.
    Mix famous events (is_offbeat: false) with hidden gems (is_offbeat: true).
    Include many Indian local festivals that tourists rarely know about."""
    
    try:
        events_data = generate_data(prompt)
        count = 0
        for e in events_data:
            try:
                event = Event(
                    name=e["name"],
                    country=e["country"],
                    city=e["city"],
                    latitude=float(e["latitude"]),
                    longitude=float(e["longitude"]),
                    start_date=date(2025, int(e["start_month"]), int(e["start_day"])),
                    end_date=date(2025, int(e["end_month"]), int(e["end_day"])),
                    type=e["type"],
                    description=e["description"],
                    popularity_score=float(e["popularity_score"]),
                    is_offbeat=bool(e["is_offbeat"]),
                )
                db.add(event)
                count += 1
            except Exception as err:
                print(f"  ⚠️ Skipped event {e.get('name')}: {err}")
        
        db.commit()
        print(f"  ✅ Seeded {count} events")
    except Exception as err:
        print(f"  ❌ Events failed: {err}")


def seed_treks(db):
    print("🥾 Generating treks data...")
    
    prompt = """Generate 30 real hiking and trekking trails as a JSON array.
    Include famous AND hidden trails from Nepal, India, Patagonia, 
    Iceland, New Zealand, Europe, USA, Africa.
    
    Each object must have exactly these fields:
    {
        "name": "trek name",
        "country": "country name",
        "latitude": 00.0000,
        "longitude": 00.0000,
        "difficulty": "easy OR medium OR hard OR extreme",
        "best_month_start": 1-12,
        "best_month_end": 1-12,
        "description": "2-3 sentences describing this trek vividly",
        "distance_km": number,
        "duration_days": number,
        "popularity_score": 0.0-1.0,
        "terrain_type": "mountain OR desert OR forest OR snow OR coastal OR valley",
        "is_offbeat": true or false
    }
    
    Make sure coordinates point to the actual trail location.
    Include many Indian Himalayan treks and Northeast India hidden trails."""
    
    try:
        treks_data = generate_data(prompt)
        count = 0
        for t in treks_data:
            try:
                trek = Trek(
                    name=t["name"],
                    country=t["country"],
                    latitude=float(t["latitude"]),
                    longitude=float(t["longitude"]),
                    difficulty=t["difficulty"],
                    best_month_start=int(t["best_month_start"]),
                    best_month_end=int(t["best_month_end"]),
                    description=t["description"],
                    distance_km=float(t["distance_km"]),
                    duration_days=int(t["duration_days"]),
                    popularity_score=float(t["popularity_score"]),
                    terrain_type=t["terrain_type"],
                    is_offbeat=bool(t["is_offbeat"]),
                )
                db.add(trek)
                count += 1
            except Exception as err:
                print(f"  ⚠️ Skipped trek {t.get('name')}: {err}")
        
        db.commit()
        print(f"  ✅ Seeded {count} treks")
    except Exception as err:
        print(f"  ❌ Treks failed: {err}")


def seed_offroad(db):
    print("🚙 Generating off-road trails data...")
    
    prompt = """Generate 30 real off-road driving routes as a JSON array.
    Include Jeep trails, 4x4 routes, motorcycle routes, scooty routes from
    India (Ladakh, Spiti, Northeast), Iceland, Patagonia, Morocco, 
    USA (Moab), Australia (Outback), New Zealand.
    
    Each object must have exactly these fields:
    {
        "name": "trail name",
        "country": "country name",
        "latitude": 00.0000,
        "longitude": 00.0000,
        "vehicle_type": "jeep OR motorcycle OR scooty OR 4x4",
        "terrain_type": "mountain OR desert OR forest OR snow OR coastal OR valley",
        "difficulty": "easy OR medium OR hard OR extreme",
        "road_condition": "paved OR unpaved OR rocky OR muddy OR seasonal",
        "best_month_start": 1-12,
        "best_month_end": 1-12,
        "description": "2-3 sentences describing this route vividly",
        "distance_km": number,
        "popularity_score": 0.0-1.0,
        "is_offbeat": true or false
    }
    
    Include famous Indian routes like Manali-Leh, Spiti Valley, 
    Meghalaya forest roads, Ziro Valley roads."""
    
    try:
        offroad_data = generate_data(prompt)
        count = 0
        for o in offroad_data:
            try:
                trail = OffroadTrail(
                    name=o["name"],
                    country=o["country"],
                    latitude=float(o["latitude"]),
                    longitude=float(o["longitude"]),
                    vehicle_type=o["vehicle_type"],
                    terrain_type=o["terrain_type"],
                    difficulty=o["difficulty"],
                    road_condition=o["road_condition"],
                    best_month_start=int(o["best_month_start"]),
                    best_month_end=int(o["best_month_end"]),
                    description=o["description"],
                    distance_km=float(o["distance_km"]),
                    popularity_score=float(o["popularity_score"]),
                    is_offbeat=bool(o["is_offbeat"]),
                )
                db.add(trail)
                count += 1
            except Exception as err:
                print(f"  ⚠️ Skipped trail {o.get('name')}: {err}")
        
        db.commit()
        print(f"  ✅ Seeded {count} off-road trails")
    except Exception as err:
        print(f"  ❌ Off-road failed: {err}")


def seed_destinations(db):
    print("🌍 Generating destinations data...")
    
    prompt = """Generate 30 travel destinations as a JSON array.
    Include famous AND hidden destinations from every continent.
    Focus on adventure, nature, culture destinations.
    Include many offbeat Indian destinations tourists rarely visit.
    
    Each object must have exactly these fields:
    {
        "name": "destination name",
        "country": "country name",
        "latitude": 00.0000,
        "longitude": 00.0000,
        "description": "2-3 sentences describing this place vividly",
        "best_month_start": 1-12,
        "best_month_end": 1-12,
        "is_offbeat": true or false,
        "tags": ["tag1", "tag2", "tag3"]
    }
    
    Tags should be from: mountains, beaches, forest, desert, snow, 
    waterfall, culture, history, food, spiritual, adventure, wildlife,
    offbeat, photography, jeep, trekking, festivals"""
    
    try:
        dest_data = generate_data(prompt)
        count = 0
        for d in dest_data:
            try:
                dest = Destination(
                    name=d["name"],
                    country=d["country"],
                    latitude=float(d["latitude"]),
                    longitude=float(d["longitude"]),
                    description=d["description"],
                    best_month_start=int(d["best_month_start"]),
                    best_month_end=int(d["best_month_end"]),
                    is_offbeat=bool(d["is_offbeat"]),
                    tags=d["tags"],
                )
                db.add(dest)
                count += 1
            except Exception as err:
                print(f"  ⚠️ Skipped destination {d.get('name')}: {err}")
        
        db.commit()
        print(f"  ✅ Seeded {count} destinations")
    except Exception as err:
        print(f"  ❌ Destinations failed: {err}")


def seed_from_datasets(db):
    import pandas as pd
    
    print("📂 Importing from datasets...")

    # ── Worldwide Cities Dataset (has coordinates) ──────────────
    try:
        df = pd.read_csv("backend/datasets/Worldwide Travel Cities Dataset (Ratings and Climate).csv")
        count = 0
        for _, row in df.iterrows():
            try:
                # build tags from ratings
                tags = []
                if row.get("culture", 0) >= 4:     tags.append("culture")
                if row.get("adventure", 0) >= 4:   tags.append("adventure")
                if row.get("nature", 0) >= 4:      tags.append("nature")
                if row.get("beaches", 0) >= 4:     tags.append("beaches")
                if row.get("nightlife", 0) >= 4:   tags.append("nightlife")
                if row.get("cuisine", 0) >= 4:     tags.append("food")
                if row.get("wellness", 0) >= 4:    tags.append("wellness")
                if row.get("seclusion", 0) >= 4:   tags.append("hidden_places")

                # popularity from urban score
                urban = float(row.get("urban", 3))
                popularity = round(urban / 5.0, 2)

                # is offbeat if seclusion is high
                is_offbeat = int(row.get("seclusion", 0)) >= 4

                dest = Destination(
                    name=str(row["city"]),
                    country=str(row["country"]),
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    description=str(row.get("short_description", "")),
                    is_offbeat=is_offbeat,
                    tags=tags if tags else ["travel"],
                )
                db.add(dest)
                count += 1
            except Exception as err:
                pass

        db.commit()
        print(f"  ✅ Imported {count} destinations from Worldwide Cities dataset")
    except Exception as e:
        print(f"  ❌ Worldwide Cities import failed: {e}")

    # ── Travel Destinations CSV ──────────────────────────────────
    try:
        df2 = pd.read_csv("backend/datasets/travel_destinations.csv")
        count2 = 0
        for _, row in df2.iterrows():
            try:
                # parse tags from category string
                category = str(row.get("Category", ""))
                tags = [t.strip() for t in category.split(",")][:5]

                # parse best months
                month_map = {
                    "Jan":1,"Feb":2,"Mar":3,"Apr":4,
                    "May":5,"Jun":6,"Jul":7,"Aug":8,
                    "Sep":9,"Oct":10,"Nov":11,"Dec":12
                }
                best_time = str(row.get("Best_Time_to_Travel", ""))
                months = [
                    month_map[m.strip()]
                    for m in best_time.split(",")
                    if m.strip() in month_map
                ]
                best_start = min(months) if months else 1
                best_end   = max(months) if months else 12

                dest2 = Destination(
                    name=str(row["City"]),
                    country=str(row["Country"]),
                    latitude=0.0,   # no coordinates in this dataset
                    longitude=0.0,
                    description=f"A wonderful destination in {row['Country']} known for {category[:100]}",
                    best_month_start=best_start,
                    best_month_end=best_end,
                    is_offbeat=False,
                    tags=tags,
                )
                db.add(dest2)
                count2 += 1
            except Exception as err:
                pass

        db.commit()
        print(f"  Imported {count2} destinations from Travel Destinations dataset")
    except Exception as e:
        print(f"  Travel Destinations import failed: {e}")


def seed_from_json_files(db):
    import json
    print("📁 Importing from JSON files...")

    # ── ALL EVENT FILES ──────────────────────────────
    event_files = [
        "data/events_data.json",
        "data/india_local_festivals.json",
        "data/world_festivals_extra.json",
    ]

    total_events = 0
    for filepath in event_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                events_data = json.load(f)
            count = 0
            for e in events_data:
                try:
                    event_type = str(e["type"]).lower().strip()
                    if event_type not in VALID_EVENT_TYPES:
                        event_type = TYPE_MAP.get(event_type, "cultural")

                    # fix end_day > 28 safety
                    start_day = min(int(e["start_day"]), 28)
                    end_day   = min(int(e["end_day"]), 28)
                    start_month = int(e["start_month"])
                    end_month   = int(e["end_month"])

                    # if end month < start month it wraps to next year — use same month
                    if end_month < start_month:
                        end_month = start_month

                    event = Event(
                        name=e["name"],
                        country=e["country"],
                        city=e["city"],
                        latitude=float(e["latitude"]),
                        longitude=float(e["longitude"]),
                        start_date=date(2025, start_month, start_day),
                        end_date=date(2025, end_month, end_day),
                        type=event_type,
                        description=e["description"],
                        popularity_score=float(e["popularity_score"]),
                        is_offbeat=bool(e["is_offbeat"]),
                    )
                    db.add(event)
                    count += 1
                except Exception as err:
                    print(f"  ⚠️ Skipped {e.get('name')}: {err}")
            db.commit()
            total_events += count
            print(f"  ✅ {filepath.split('/')[-1]} → {count} events")
        except Exception as e:
            db.rollback()
            print(f"  ❌ {filepath} failed: {e}")

    print(f"  🎪 Total events imported: {total_events}")

    # ── TREKS ────────────────────────────────────────
    try:
        with open("data/treks_data.json", "r", encoding="utf-8") as f:
            treks_data = json.load(f)
        count = 0
        for t in treks_data:
            try:
                trek = Trek(
                    name=t["name"],
                    country=t["country"],
                    latitude=float(t["latitude"]),
                    longitude=float(t["longitude"]),
                    difficulty=t["difficulty"],
                    best_month_start=int(t["best_month_start"]),
                    best_month_end=int(t["best_month_end"]),
                    description=t["description"],
                    distance_km=float(t["distance_km"]),
                    duration_days=int(t["duration_days"]),
                    popularity_score=float(t["popularity_score"]),
                    terrain_type=t["terrain_type"],
                    is_offbeat=bool(t["is_offbeat"]),
                )
                db.add(trek)
                count += 1
            except Exception as err:
                print(f"  ⚠️ Skipped trek {t.get('name')}: {err}")
        db.commit()
        print(f"  ✅ treks_data.json → {count} treks")
    except Exception as e:
        db.rollback()
        print(f"  ❌ Treks JSON failed: {e}")

    # ── OFFROAD ──────────────────────────────────────
    try:
        with open("data/offroad_data.json", "r", encoding="utf-8") as f:
            offroad_data = json.load(f)
        count = 0
        for o in offroad_data:
            try:
                trail = OffroadTrail(
                    name=o["name"],
                    country=o["country"],
                    latitude=float(o["latitude"]),
                    longitude=float(o["longitude"]),
                    vehicle_type=o["vehicle_type"],
                    terrain_type=o["terrain_type"],
                    difficulty=o["difficulty"],
                    road_condition=o["road_condition"],
                    best_month_start=int(o["best_month_start"]),
                    best_month_end=int(o["best_month_end"]),
                    description=o["description"],
                    distance_km=float(o["distance_km"]),
                    popularity_score=float(o["popularity_score"]),
                    is_offbeat=bool(o["is_offbeat"]),
                )
                db.add(trail)
                count += 1
            except Exception as err:
                print(f"  ⚠️ Skipped trail {o.get('name')}: {err}")
        db.commit()
        print(f"  ✅ offroad_data.json → {count} offroad trails")
    except Exception as e:
        db.rollback()
        print(f"  ❌ Offroad JSON failed: {e}")


def run_seed():
    print("\n🌍 WANDERLUST AI — DATA SEEDING PIPELINE")
    print("=" * 50)

    db = SessionLocal()

    existing_events  = db.query(Event).count()
    existing_treks   = db.query(Trek).count()
    existing_offroad = db.query(OffroadTrail).count()

    print(f"Existing: {existing_events} events, {existing_treks} treks, {existing_offroad} offroad")

    # datasets
    try:
        seed_from_datasets(db)
    except Exception as e:
        print(f"❌ Datasets failed: {e}")
        db.rollback()

    # JSON files — only if events < 200
    if existing_events < 200:
        seed_from_json_files(db)
    else:
        print(f"⏭️ Skipping JSON files — already have {existing_events} events")

    # Mistral — only if still low
    if existing_events < 50:
        try:
            seed_events(db)
        except Exception as e:
            db.rollback()

    if existing_treks < 50:
        try:
            seed_treks(db)
        except Exception as e:
            db.rollback()

    if existing_offroad < 50:
        try:
            seed_offroad(db)
        except Exception as e:
            db.rollback()

    db.close()

    # final count
    db2 = SessionLocal()
    print(f"\n📊 FINAL DATABASE COUNT:")
    print(f"  Events:       {db2.query(Event).count()}")
    print(f"  Treks:        {db2.query(Trek).count()}")
    print(f"  Offroad:      {db2.query(OffroadTrail).count()}")
    print(f"  Destinations: {db2.query(Destination).count()}")
    db2.close()

    print("\n" + "=" * 50)
    print("✅ SEEDING COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    run_seed()