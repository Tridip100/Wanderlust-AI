from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from backend.db.connection import get_db
from backend.db.models import (
    User, UserTravelerType, UserInterest,
    UserTravelVibe, UserTripPreference
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


class OnboardingData(BaseModel):
    user_id: str
    traveler_types: List[str]
    interests: List[str]
    travel_vibes: List[str]
    trip_preference: str


class ProfileUpdate(BaseModel):
    traveler_types: List[str]
    interests: List[str]
    travel_vibes: List[str]
    trip_preference: str


@router.get("/{user_id}")
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "User not found"}

    traveler_types = [
        t.traveler_type for t in
        db.query(UserTravelerType).filter(
            UserTravelerType.user_id == user_id
        ).all()
    ]

    interests = [
        i.interest for i in
        db.query(UserInterest).filter(
            UserInterest.user_id == user_id
        ).all()
    ]

    travel_vibes = [
        v.vibe for v in
        db.query(UserTravelVibe).filter(
            UserTravelVibe.user_id == user_id
        ).all()
    ]

    trip_preference = db.query(UserTripPreference).filter(
        UserTripPreference.user_id == user_id
    ).first()

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "profile_picture": user.profile_picture,
        "onboarding_complete": user.onboarding_complete,
        "traveler_types": traveler_types,
        "interests": interests,
        "travel_vibes": travel_vibes,
        "trip_preference": trip_preference.trip_type if trip_preference else None,
        "created_at": str(user.created_at),
        "last_login": str(user.last_login) if user.last_login else None,
    }


@router.post("/onboarding")
def complete_onboarding(data: OnboardingData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        return {"error": "User not found"}

    # clear existing preferences
    db.query(UserTravelerType).filter(
        UserTravelerType.user_id == data.user_id
    ).delete()
    db.query(UserInterest).filter(
        UserInterest.user_id == data.user_id
    ).delete()
    db.query(UserTravelVibe).filter(
        UserTravelVibe.user_id == data.user_id
    ).delete()
    db.query(UserTripPreference).filter(
        UserTripPreference.user_id == data.user_id
    ).delete()

    # save new traveler types
    for t in data.traveler_types:
        db.add(UserTravelerType(user_id=data.user_id, traveler_type=t))

    # save new interests
    for i in data.interests:
        db.add(UserInterest(user_id=data.user_id, interest=i))

    # save new travel vibes
    for v in data.travel_vibes:
        db.add(UserTravelVibe(user_id=data.user_id, vibe=v))

    # save trip preference
    db.add(UserTripPreference(
        user_id=data.user_id,
        trip_type=data.trip_preference
    ))

    # mark onboarding complete
    user.onboarding_complete = True
    db.commit()

    return {"message": "Onboarding complete ✅"}


@router.put("/{user_id}/profile")
def update_profile(
    user_id: str,
    data: ProfileUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "User not found"}

    # clear existing preferences
    db.query(UserTravelerType).filter(
        UserTravelerType.user_id == user_id
    ).delete()
    db.query(UserInterest).filter(
        UserInterest.user_id == user_id
    ).delete()
    db.query(UserTravelVibe).filter(
        UserTravelVibe.user_id == user_id
    ).delete()
    db.query(UserTripPreference).filter(
        UserTripPreference.user_id == user_id
    ).delete()

    # save updated preferences
    for t in data.traveler_types:
        db.add(UserTravelerType(user_id=user_id, traveler_type=t))

    for i in data.interests:
        db.add(UserInterest(user_id=user_id, interest=i))

    for v in data.travel_vibes:
        db.add(UserTravelVibe(user_id=user_id, vibe=v))

    db.add(UserTripPreference(
        user_id=user_id,
        trip_type=data.trip_preference
    ))

    db.commit()

    return {"message": "Profile updated ✅"}