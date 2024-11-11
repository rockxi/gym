# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models, schemas, crud, dependencies
from .database import engine
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gym Tracker API")

# Разрешение CORS (опционально)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Замените на актуальные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Маршрут для регистрации пользователей
@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# Маршрут для получения токена (упрощённо, использовать более безопасный метод в продакшене)
@app.post("/token", response_model=schemas.UserResponse)
def login(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user or not crud.pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return db_user

# CRUD для упражнений
@app.post("/exercises/", response_model=schemas.ExerciseResponse)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    return crud.create_exercise(db=db, user_id=current_user.id, exercise=exercise)

from typing import List

@app.get("/exercises/", response_model=List[schemas.ExerciseResponse])
def read_exercises(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    exercises = crud.get_exercises(db, user_id=current_user.id, skip=skip, limit=limit)
    return exercises

@app.get("/exercises/{exercise_id}", response_model=schemas.ExerciseResponse)
def read_exercise(exercise_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    db_exercise = crud.get_exercise(db, user_id=current_user.id, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise

@app.put("/exercises/{exercise_id}", response_model=schemas.ExerciseResponse)
def update_exercise(exercise_id: int, exercise: schemas.ExerciseUpdate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    db_exercise = crud.get_exercise(db, user_id=current_user.id, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return crud.update_exercise(db=db, db_exercise=db_exercise, exercise=exercise)

@app.delete("/exercises/{exercise_id}", status_code=204)
def delete_exercise(exercise_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    db_exercise = crud.get_exercise(db, user_id=current_user.id, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    crud.delete_exercise(db=db, db_exercise=db_exercise)
    return

# CRUD для подходов (sets)
@app.post("/exercises/{exercise_id}/sets/", response_model=schemas.SetResponse)
def create_set_for_exercise(exercise_id: int, set: schemas.SetCreate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    db_exercise = crud.get_exercise(db, user_id=current_user.id, exercise_id=exercise_id)
    if db_exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return crud.create_set(db=db, user_id=current_user.id, exercise_id=exercise_id, set=set)

@app.put("/exercises/{exercise_id}/sets/{set_id}", response_model=schemas.SetResponse)
def update_set_for_exercise(exercise_id: int, set_id: int, set: schemas.SetUpdate, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    db_set = crud.get_set(db, user_id=current_user.id, exercise_id=exercise_id, set_id=set_id)
    if db_set is None:
        raise HTTPException(status_code=404, detail="Set not found")
    return crud.update_set(db=db, db_set=db_set, set=set)

@app.delete("/exercises/{exercise_id}/sets/{set_id}", status_code=204)
def delete_set_for_exercise(exercise_id: int, set_id: int, db: Session = Depends(dependencies.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
    db_set = crud.get_set(db, user_id=current_user.id, exercise_id=exercise_id, set_id=set_id)
    if db_set is None:
        raise HTTPException(status_code=404, detail="Set not found")
    crud.delete_set(db=db, db_set=db_set)
    return