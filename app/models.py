# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)

    exercises = relationship("Exercise", back_populates="owner")


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="exercises")
    sets = relationship("Set", back_populates="exercise", cascade="all, delete-orphan")


class Set(Base):
    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, nullable=False)
    repetitions = Column(Integer, nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))

    exercise = relationship("Exercise", back_populates="sets")