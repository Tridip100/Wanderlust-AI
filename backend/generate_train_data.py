"""
Wanderlust AI — Synthetic Training Data Generator
===================================================
Pulls real records from your PostgreSQL DB (events, treks, destinations)
and generates synthetic user-item pairs with logical recommendation scores.

Output: data/ml_training_data.csv (~10,000+ rows)

Run: python generate_training_data.py
"""

import os
import random
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# ─── DB Connection ────────────────────────────────────────────────
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/wanderlust_ai")

def get_connection():
    return psycopg2.connect(DB_URL)

# ─── User Profile Definitions ─────────────────────────────────────
USER_TYPES      = ["solo", "couple", "family"]
INTERESTS       = ["adventure", "culture", "nature", "food", "offbeat", "spiritual"]
VIBES           = ["relaxed", "thrill", "spiritual", "luxury", "budget", "offbeat"]
BUDGET_RANGES   = {
    "budget":  (50,  500),
    "mid":     (500, 2000),
    "luxury":  (2000, 8000),
}
MONTHS = list(range(1, 13))

# ─── Scoring Logic ────────────────────────────────────────────────

MONTH_NAMES = {
    1:"January",2:"February",3:"March",4:"April",
    5:"May",6:"June",7:"July",8:"August",
    9:"September",10:"October",11:"November",12:"December"
}

def month_match_score(best_month_str: str, user_month: int) -> float:
    """Score how well the item's best month matches the user's travel month."""
    if not best_month_str:
        return 0.5
    best_month_str = str(best_month_str).lower()
    user_month_name = MONTH_NAMES[user_month].lower()
    # Check direct match
    if user_month_name in best_month_str or str(user_month) in best_month_str:
        return 1.0
    # Adjacent months are okay
    for offset in [-1, 1]:
        adj = MONTH_NAMES.get((user_month - 1 + offset) % 12 + 1, "").lower()
        if adj in best_month_str:
            return 0.7
    return 0.2

def month_range_match(start_month, end_month, user_month: int) -> float:
    """Score based on a month range (best_month_start to best_month_end)."""
    try:
        s = int(start_month) if start_month else 1
        e = int(end_month) if end_month else 12
    except:
        return 0.5
    if s <= e:
        if s <= user_month <= e:
            return 1.0
        if user_month == s - 1 or user_month == e + 1:
            return 0.65
        return 0.2
    else:  # wraps year e.g. Nov→Feb
        if user_month >= s or user_month <= e:
            return 1.0
        return 0.2

def difficulty_match(difficulty: str, user_type: str, vibe: str) -> float:
    """Match trek difficulty to user profile."""
    if not difficulty:
        return 0.5
    d = difficulty.lower()
    if user_type == "family":
        return 1.0 if d == "easy" else (0.5 if d == "moderate" else 0.1)
    if user_type == "couple":
        return 0.6 if d == "easy" else (1.0 if d == "moderate" else 0.7)
    if user_type == "solo":
        if vibe == "thrill":
            return 0.4 if d == "easy" else (0.8 if d == "moderate" else 1.0)
        return 0.8 if d == "easy" else (1.0 if d == "moderate" else 0.6)
    return 0.5

def interest_match(item_type: str, item_tags: str, user_interest: str, user_vibe: str) -> float:
    """Match item type/tags to user interest."""
    score = 0.3  # base
    combined = f"{item_type} {item_tags}".lower() if item_tags else str(item_type).lower()

    interest_keywords = {
        "adventure":  ["trek", "trail", "offroad", "hike", "mountain", "jeep", "4x4", "extreme"],
        "culture":    ["festival", "heritage", "temple", "museum", "art", "tradition", "cultural"],
        "nature":     ["forest", "waterfall", "lake", "wildlife", "national park", "beach", "river"],
        "food":       ["food", "cuisine", "market", "street food", "culinary"],
        "offbeat":    ["hidden", "offbeat", "remote", "unexplored", "secret", "local"],
        "spiritual":  ["temple", "pilgrimage", "spiritual", "monastery", "sacred", "meditation"],
    }
    vibe_keywords = {
        "relaxed":   ["resort", "beach", "spa", "easy", "calm"],
        "thrill":    ["extreme", "hard", "adventure", "offroad", "summit"],
        "spiritual": ["temple", "meditation", "sacred", "pilgrimage"],
        "luxury":    ["luxury", "premium", "resort", "hotel"],
        "budget":    ["budget", "hostel", "camping", "backpacker"],
        "offbeat":   ["hidden", "remote", "offbeat", "local"],
    }

    for kw in interest_keywords.get(user_interest, []):
        if kw in combined:
            score += 0.15
    for kw in vibe_keywords.get(user_vibe, []):
        if kw in combined:
            score += 0.1

    return min(score, 1.0)

def offbeat_bonus(is_offbeat: bool, user_interest: str, user_vibe: str) -> float:
    if is_offbeat and user_interest == "offbeat":
        return 0.15
    if is_offbeat and user_vibe == "offbeat":
        return 0.10
    if not is_offbeat and user_interest == "offbeat":
        return -0.05
    return 0.0

def budget_match(avg_cost: float, user_budget: float) -> float:
    if not avg_cost or avg_cost == 0:
        return 0.5
    ratio = user_budget / avg_cost
    if ratio >= 2.0:   return 1.0   # very affordable
    if ratio >= 1.2:   return 0.85
    if ratio >= 0.9:   return 0.65  # tight but doable
    if ratio >= 0.6:   return 0.35  # over budget
    return 0.1                       # way over budget

def compute_score(pop_score, season_score, diff_score, interest_score, offbeat_b, budget_score) -> float:
    raw = (
        pop_score      * 0.25 +
        season_score   * 0.25 +
        diff_score     * 0.15 +
        interest_score * 0.20 +
        budget_score   * 0.15 +
        offbeat_b
    )
    # Add small noise for realism
    noise = random.uniform(-0.04, 0.04)
    return round(min(max(raw + noise, 0.0), 1.0), 4)

# ─── Fetch Real Data from DB ──────────────────────────────────────

def fetch_events(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, country, city, latitude, longitude,
               type, popularity_score, start_date
        FROM events
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        LIMIT 387
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]

def fetch_treks(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, country, latitude, longitude,
               difficulty, best_month_start, best_month_end,
               popularity_score, is_offbeat, terrain_type
        FROM treks
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        LIMIT 180
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]

def fetch_destinations(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, country, latitude, longitude,
        best_month_start, best_month_end,
        tags,
        COALESCE(is_offbeat, false) as is_offbeat
        FROM destinations
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        LIMIT 2000
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]

# ─── Generate Training Rows ───────────────────────────────────────

def generate_rows_for_events(events, n_users=15):
    rows = []
    for event in events:
        for _ in range(n_users):
            user_type    = random.choice(USER_TYPES)
            interest     = random.choice(INTERESTS)
            vibe         = random.choice(VIBES)
            budget_tier  = random.choice(list(BUDGET_RANGES.keys()))
            budget       = random.uniform(*BUDGET_RANGES[budget_tier])
            travel_month = random.randint(1, 12)

            pop    = float(event.get("popularity_score") or 0.5)
            season = month_match_score(
                str(event.get("start_date", "")) if event.get("start_date") else "",
                travel_month
            )
            diff   = 0.7  # events don't have difficulty — neutral-good
            inter  = interest_match(
                event.get("type", "event"), "", interest, vibe
            )
            ob     = offbeat_bonus(False, interest, vibe)
            bud    = budget_match(200, budget)  # avg event cost assumption

            score = compute_score(pop, season, diff, inter, ob, bud)

            rows.append({
                "item_id":           event["id"],
                "item_type":         "event",
                "item_name":         event.get("name", ""),
                "country":           event.get("country", ""),
                "user_type":         user_type,
                "interest":          interest,
                "vibe":              vibe,
                "budget_usd":        round(budget, 2),
                "travel_month":      travel_month,
                "popularity_score":  round(pop, 4),
                "season_match":      round(season, 4),
                "difficulty_match":  round(diff, 4),
                "interest_match":    round(inter, 4),
                "budget_match":      round(bud, 4),
                "is_offbeat":        0,
                "recommendation_score": score,
            })
    return rows

def generate_rows_for_treks(treks, n_users=20):
    rows = []
    for trek in treks:
        for _ in range(n_users):
            user_type    = random.choice(USER_TYPES)
            interest     = random.choice(INTERESTS)
            vibe         = random.choice(VIBES)
            budget_tier  = random.choice(list(BUDGET_RANGES.keys()))
            budget       = random.uniform(*BUDGET_RANGES[budget_tier])
            travel_month = random.randint(1, 12)

            pop    = float(trek.get("popularity_score") or 0.5)
            season = month_range_match(trek.get("best_month_start"), trek.get("best_month_end"), travel_month)
            diff   = difficulty_match(trek.get("difficulty", ""), user_type, vibe)
            terrain = f"trek adventure mountain hike {trek.get('terrain_type', '')}"
            inter  = interest_match("trek", terrain, interest, vibe)
            is_ob  = bool(trek.get("is_offbeat", False))
            ob     = offbeat_bonus(is_ob, interest, vibe)
            bud    = budget_match(300, budget)

            score = compute_score(pop, season, diff, inter, ob, bud)

            rows.append({
                "item_id":           trek["id"],
                "item_type":         "trek",
                "item_name":         trek.get("name", ""),
                "country":           trek.get("country", ""),
                "user_type":         user_type,
                "interest":          interest,
                "vibe":              vibe,
                "budget_usd":        round(budget, 2),
                "travel_month":      travel_month,
                "popularity_score":  round(pop, 4),
                "season_match":      round(season, 4),
                "difficulty_match":  round(diff, 4),
                "interest_match":    round(inter, 4),
                "budget_match":      round(bud, 4),
                "is_offbeat":        int(is_ob),
                "recommendation_score": score,
            })
    return rows

def generate_rows_for_destinations(destinations, n_users=10):
    rows = []
    for dest in destinations:
        for _ in range(n_users):
            user_type    = random.choice(USER_TYPES)
            interest     = random.choice(INTERESTS)
            vibe         = random.choice(VIBES)
            budget_tier  = random.choice(list(BUDGET_RANGES.keys()))
            budget       = random.uniform(*BUDGET_RANGES[budget_tier])
            travel_month = random.randint(1, 12)

            pop    = 0.5

            season = month_range_match(
                dest.get("best_month_start"),
                dest.get("best_month_end"),
                travel_month
            )
            diff   = 0.6  # destinations neutral difficulty
            inter  = interest_match(
                dest.get("tags", "") or "",
                dest.get("tags", "") or "",
                interest, vibe
            )
            is_ob  = bool(dest.get("is_offbeat", False))
            ob     = offbeat_bonus(is_ob, interest, vibe)
            bud    = budget_match(500, budget)

            score = compute_score(pop, season, diff, inter, ob, bud)

            rows.append({
                "item_id":           dest["id"],
                "item_type":         "destination",
                "item_name":         dest.get("name", ""),
                "country":           dest.get("country", ""),
                "user_type":         user_type,
                "interest":          interest,
                "vibe":              vibe,
                "budget_usd":        round(budget, 2),
                "travel_month":      travel_month,
                "popularity_score":  round(pop, 4),
                "season_match":      round(season, 4),
                "difficulty_match":  round(diff, 4),
                "interest_match":    round(inter, 4),
                "budget_match":      round(bud, 4),
                "is_offbeat":        int(is_ob),
                "recommendation_score": score,
            })
    return rows

# ─── Main ─────────────────────────────────────────────────────────

def main():
    print("🔌 Connecting to DB...")
    conn = get_connection()

    print("📦 Fetching events...")
    events = fetch_events(conn)
    print(f"   → {len(events)} events fetched")

    print("📦 Fetching treks...")
    treks = fetch_treks(conn)
    print(f"   → {len(treks)} treks fetched")

    print("📦 Fetching destinations...")
    destinations = fetch_destinations(conn)
    print(f"   → {len(destinations)} destinations fetched")

    conn.close()

    print("\n⚙️  Generating synthetic rows...")
    all_rows = []
    all_rows += generate_rows_for_events(events, n_users=15)
    all_rows += generate_rows_for_treks(treks, n_users=20)
    all_rows += generate_rows_for_destinations(destinations, n_users=10)

    random.shuffle(all_rows)

    print(f"   → Total rows generated: {len(all_rows)}")

    # Save CSV
    os.makedirs("data", exist_ok=True)
    output_path = "data/ml_training_data.csv"

    fieldnames = [
        "item_id", "item_type", "item_name", "country",
        "user_type", "interest", "vibe", "budget_usd", "travel_month",
        "popularity_score", "season_match", "difficulty_match",
        "interest_match", "budget_match", "is_offbeat",
        "recommendation_score"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✅ Done! Saved to: {output_path}")
    print(f"📊 Stats:")
    print(f"   Events rows:       {len([r for r in all_rows if r['item_type']=='event'])}")
    print(f"   Trek rows:         {len([r for r in all_rows if r['item_type']=='trek'])}")
    print(f"   Destination rows:  {len([r for r in all_rows if r['item_type']=='destination'])}")
    print(f"   TOTAL:             {len(all_rows)}")
    print(f"\n💡 Next: run train_model.py to train XGBoost on this data.")

if __name__ == "__main__":
    main()
