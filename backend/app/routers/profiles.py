from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas, auth as auth_utils
from app.services.resume_parser import extract_resume_facts, format_resume_summary

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


@router.post("/", response_model=schemas.ProfileOut)
def create_profile(
    profile: schemas.ProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    db_profile = models.Profile(user_id=current_user.id, **profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/", response_model=List[schemas.ProfileOut])
def list_profiles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    return db.query(models.Profile).filter(models.Profile.user_id == current_user.id).all()


@router.get("/{profile_id}", response_model=schemas.ProfileOut)
def get_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    profile = db.query(models.Profile).filter(
        models.Profile.id == profile_id,
        models.Profile.user_id == current_user.id,
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{profile_id}", response_model=schemas.ProfileOut)
def update_profile(
    profile_id: str,
    profile: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    db_profile = db.query(models.Profile).filter(
        models.Profile.id == profile_id,
        models.Profile.user_id == current_user.id,
    ).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in profile.model_dump(exclude_unset=True).items():
        setattr(db_profile, key, value)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    db_profile = db.query(models.Profile).filter(
        models.Profile.id == profile_id,
        models.Profile.user_id == current_user.id,
    ).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    db.delete(db_profile)
    db.commit()
    return None


@router.post("/{profile_id}/extract-resume", response_model=schemas.ProfileOut)
async def extract_resume(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    db_profile = db.query(models.Profile).filter(
        models.Profile.id == profile_id,
        models.Profile.user_id == current_user.id,
    ).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if not db_profile.resume_text:
        raise HTTPException(status_code=400, detail="Profile has no resume text")

    facts = await extract_resume_facts(db_profile.resume_text)
    db_profile.resume_summary = format_resume_summary(facts)
    db.commit()
    db.refresh(db_profile)
    return db_profile
