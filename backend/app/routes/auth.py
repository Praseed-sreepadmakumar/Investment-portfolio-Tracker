from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.auth import hash_password 

router = APIRouter()
@router.post("/register")
def register_user(user: UserCreate):
    db: Session = SessionLocal()
    try:
        hashed_pw = hash_password(user.password)
        new_user = User(
            username=user.username, 
            email=user.email, 
            password=hashed_pw
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "message": "User registered successfully",
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )
    finally:
        db.close()