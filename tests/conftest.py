# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from app.dependencies import get_db

# Настройте строку подключения к тестовой базе данных
SQLALCHEMY_DATABASE_URL = "postgresql://r:kj@localhost/gym_tracker"

# Создайте движок и сессию для тестовой базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создайте таблицы в тестовой базе данных перед запуском тестов
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.drop_all(bind=engine)  # Очистка базы данных перед тестами
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)  # Очистка после тестов

# Фикстура для предоставления сессии базы данных в тестах
@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Фикстура для переопределения зависимости get_db в приложении
@pytest.fixture
def client():
    # Переопределяем зависимость get_db для использования тестовой базы данных
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()