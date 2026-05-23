import uuid
from sqlalchemy import (
    Column, String, Boolean,
    Float, Integer, Text,
    DateTime, Date, ForeignKey, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.db.connection import Base


# ──────────────────────────────────────────────
# 1. USERS
# ──────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    profile_picture = Column(Text)
    google_id = Column(String(255), unique=True, nullable=False)
    travel_style = Column(String(50))
    onboarding_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)

    # relationships
    traveler_types = relationship("UserTravelerType", back_populates="user", cascade="all, delete")
    interests = relationship("UserInterest", back_populates="user", cascade="all, delete")
    travel_vibes = relationship("UserTravelVibe", back_populates="user", cascade="all, delete")
    trip_preferences = relationship("UserTripPreference", back_populates="user", cascade="all, delete")
    wishlist = relationship("Wishlist", back_populates="user", cascade="all, delete")
    travel_history = relationship("TravelHistory", back_populates="user", cascade="all, delete")
    itineraries = relationship("Itinerary", back_populates="user", cascade="all, delete")
    feedback = relationship("UserFeedback", back_populates="user", cascade="all, delete")

# ──────────────────────────────────────────────
# 2. USER TRAVELER TYPES
# ──────────────────────────────────────────────
class UserTravelerType(Base):
    __tablename__ = "user_traveler_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    traveler_type = Column(String(50), nullable=False)

    # relationship back to user
    user = relationship("User", back_populates="traveler_types")


# ──────────────────────────────────────────────
# 3. USER INTERESTS
# ──────────────────────────────────────────────
class UserInterest(Base):
    __tablename__ = "user_interests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interest = Column(String(50), nullable=False)

    user = relationship("User", back_populates="interests")


# ──────────────────────────────────────────────
# 4. USER TRAVEL VIBES
# ──────────────────────────────────────────────
class UserTravelVibe(Base):
    __tablename__ = "user_travel_vibes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vibe = Column(String(50), nullable=False)

    user = relationship("User", back_populates="travel_vibes")


# ──────────────────────────────────────────────
# 5. USER TRIP PREFERENCE
# ──────────────────────────────────────────────
class UserTripPreference(Base):
    __tablename__ = "user_trip_preference"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    trip_type = Column(String(50), nullable=False)

    user = relationship("User", back_populates="trip_preferences")


# ──────────────────────────────────────────────
# 6. DESTINATIONS
# ──────────────────────────────────────────────
class Destination(Base):
    __tablename__ = "destinations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text)
    best_month_start = Column(Integer)
    best_month_end = Column(Integer)
    image_url = Column(Text)
    youtube_url = Column(Text)
    is_offbeat = Column(Boolean, default=False)
    tags = Column(ARRAY(String))
    created_at = Column(DateTime, default=func.now())


# ──────────────────────────────────────────────
# 7. EVENTS
# ──────────────────────────────────────────────
class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    popularity_score = Column(Float, default=0.5)
    image_url = Column(Text)
    youtube_url = Column(Text)
    is_offbeat = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


# ──────────────────────────────────────────────
# 8. TREKS
# ──────────────────────────────────────────────
class Trek(Base):
    __tablename__ = "treks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    difficulty = Column(String(50), nullable=False)
    best_month_start = Column(Integer, nullable=False)
    best_month_end = Column(Integer, nullable=False)
    description = Column(Text)
    distance_km = Column(Float)
    duration_days = Column(Integer)
    popularity_score = Column(Float, default=0.5)
    image_url = Column(Text)
    youtube_url = Column(Text)
    terrain_type = Column(String(50))
    is_offbeat = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


# ──────────────────────────────────────────────
# 9. OFFROAD TRAILS
# ──────────────────────────────────────────────
class OffroadTrail(Base):
    __tablename__ = "offroad_trails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    vehicle_type = Column(String(50), nullable=False)
    terrain_type = Column(String(50), nullable=False)
    difficulty = Column(String(50), nullable=False)
    road_condition = Column(String(50))
    best_month_start = Column(Integer, nullable=False)
    best_month_end = Column(Integer, nullable=False)
    description = Column(Text)
    distance_km = Column(Float)
    popularity_score = Column(Float, default=0.5)
    image_url = Column(Text)
    youtube_url = Column(Text)
    is_offbeat = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


# ──────────────────────────────────────────────
# 10. WISHLIST
# ──────────────────────────────────────────────
class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=True)
    trek_id = Column(UUID(as_uuid=True), ForeignKey("treks.id", ondelete="CASCADE"), nullable=True)
    offroad_id = Column(UUID(as_uuid=True), ForeignKey("offroad_trails.id", ondelete="CASCADE"), nullable=True)
    destination_id = Column(UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="wishlist")


# ──────────────────────────────────────────────
# 11. TRAVEL HISTORY
# ──────────────────────────────────────────────
class TravelHistory(Base):
    __tablename__ = "travel_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    trek_id = Column(UUID(as_uuid=True), ForeignKey("treks.id", ondelete="SET NULL"), nullable=True)
    offroad_id = Column(UUID(as_uuid=True), ForeignKey("offroad_trails.id", ondelete="SET NULL"), nullable=True)
    destination_id = Column(UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True)
    visited_on = Column(Date, nullable=False)
    rating = Column(Integer)
    notes = Column(Text)
    personal_tip = Column(Text)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="travel_history")


# ──────────────────────────────────────────────
# 12. ITINERARIES
# ──────────────────────────────────────────────
class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    trek_id = Column(UUID(as_uuid=True), ForeignKey("treks.id", ondelete="SET NULL"), nullable=True)
    offroad_id = Column(UUID(as_uuid=True), ForeignKey("offroad_trails.id", ondelete="SET NULL"), nullable=True)
    destination_id = Column(UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True)
    traveler_type = Column(String(50), nullable=False)
    travel_pace = Column(String(50), nullable=False)
    budget_style = Column(String(50), nullable=False)
    accommodation = Column(String(50))
    duration_days = Column(Integer, nullable=False)
    content = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="itineraries")


    # ──────────────────────────────────────────────
# 13. USER FEEDBACK
# ──────────────────────────────────────────────
class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="feedback")