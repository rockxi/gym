# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    token = secrets.token_hex(16)
    db_user = models.User(username=user.username, hashed_password=hashed_password, token=token)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, token: str):
    return db.query(models.User).filter(models.User.token == token).first()

# Exercise CRUD
def get_exercises(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Exercise).filter(models.Exercise.owner_id == user_id).offset(skip).limit(limit).all()

def get_exercise(db: Session, user_id: int, exercise_id: int):
    return db.query(models.Exercise).filter(models.Exercise.owner_id == user_id, models.Exercise.id == exercise_id).first()

def create_exercise(db: Session, user_id: int, exercise: schemas.ExerciseCreate):
    db_exercise = models.Exercise(**exercise.dict(), owner_id=user_id)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def update_exercise(db: Session, db_exercise: models.Exercise, exercise: schemas.ExerciseUpdate):
    for key, value in exercise.dict().items():
        setattr(db_exercise, key, value)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def delete_exercise(db: Session, db_exercise: models.Exercise):
    db.delete(db_exercise)
    db.commit()

# Set CRUD
def get_set(db: Session, user_id: int, exercise_id: int, set_id: int):
    return db.query(models.Set).join(models.Exercise).filter(
        models.Exercise.owner_id == user_id,
        models.Set.id == set_id,
        models.Set.exercise_id == exercise_id
    ).first()

def create_set(db: Session, user_id: int, exercise_id: int, set: schemas.SetCreate):
    db_set = models.Set(**set.dict(), exercise_id=exercise_id)
    db.add(db_set)
    db.commit()
    db.refresh(db_set)
    return db_set

def update_set(db: Session, db_set: models.Set, set: schemas.SetUpdate):
    for key, value in set.dict().items():
        setattr(db_set, key, value)
    db.commit()
    db.refresh(db_set)
    return db_set

def delete_set(db: Session, db_set: models.Set):
    db.delete(db_set)
    db.commit()