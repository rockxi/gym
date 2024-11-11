# app/dependencies.py
from .database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from . import auth, crud

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user