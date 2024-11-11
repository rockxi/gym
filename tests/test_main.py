# tests/test_main.py
import pytest

@pytest.fixture
def user_credentials():
    return {
        "username": "testuser",
        "password": "testpassword"
    }

@pytest.fixture
def auth_headers(client, user_credentials):
    # Регистрируем пользователя (если еще не зарегистрирован)
    response = client.post("/register", json=user_credentials)
    # Если пользователь уже зарегистрирован, игнорируем ошибку
    if response.status_code not in [200, 400]:
        raise Exception("Ошибка при регистрации пользователя")
    # Логинимся
    login_response = client.post("/token", json=user_credentials)
    assert login_response.status_code == 200
    token = login_response.json()["token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def create_exercise(client, auth_headers):
    exercise_data = {"name": "Приседания", "description": "Упражнение для ног"}
    response = client.post("/exercises/", json=exercise_data, headers=auth_headers)
    assert response.status_code == 200
    return response.json()["id"]

@pytest.fixture
def create_set(client, auth_headers, create_exercise):
    set_data = {"weight": 50.0, "repetitions": 10}
    response = client.post(f"/exercises/{create_exercise}/sets/", json=set_data, headers=auth_headers)
    assert response.status_code == 200
    return response.json()["id"]

def test_register_user(client, user_credentials):
    response = client.post("/register", json=user_credentials)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_credentials["username"]
    assert "id" in data
    assert "token" in data

def test_register_existing_user(client, user_credentials):
    # Попробуем зарегистрировать того же пользователя снова
    response = client.post("/register", json=user_credentials)
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_login_user(client, auth_headers):
    # Фикстура auth_headers уже обеспечивает регистрацию и логин
    # Проверим, что заголовки авторизации содержат токен
    assert "Authorization" in auth_headers
    token = auth_headers["Authorization"].split(" ")[1]
    assert len(token) > 0

def test_login_invalid_user(client):
    response = client.post("/token", json={"username": "nonexistent", "password": "wrong"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"

def test_create_exercise(client, auth_headers):
    exercise_data = {"name": "Жим лёжа", "description": "Упражнение для груди"}
    response = client.post("/exercises/", json=exercise_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == exercise_data["name"]
    assert data["description"] == exercise_data["description"]
    assert "id" in data
    assert data["sets"] == []

def test_get_exercises(client, auth_headers, create_exercise):
    response = client.get("/exercises/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # Должно быть как минимум одно упражнение

    # Проверяем структуру первого упражнения
    exercise = next((ex for ex in data if ex["id"] == create_exercise), None)
    assert exercise is not None
    assert "id" in exercise
    assert "name" in exercise
    assert "description" in exercise
    assert "sets" in exercise
    assert isinstance(exercise["sets"], list)

def test_get_exercise_by_id(client, auth_headers, create_exercise):
    exercise_id = create_exercise
    response = client.get(f"/exercises/{exercise_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == exercise_id
    assert data["name"] == "Приседания"
    assert data["description"] == "Упражнение для ног"

def test_update_exercise(client, auth_headers, create_exercise):
    exercise_id = create_exercise
    update_data = {"name": "Становая тяга", "description": "Упражнение для спины"}
    response = client.put(f"/exercises/{exercise_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == exercise_id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_delete_exercise(client, auth_headers, create_exercise):
    exercise_id = create_exercise
    response = client.delete(f"/exercises/{exercise_id}", headers=auth_headers)
    assert response.status_code == 204

    # Проверяем, что упражнение удалено
    get_response = client.get(f"/exercises/{exercise_id}", headers=auth_headers)
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Exercise not found"

def test_create_set(client, auth_headers, create_exercise):
    exercise_id = create_exercise
    set_data = {"weight": 50.0, "repetitions": 10}
    response = client.post(f"/exercises/{exercise_id}/sets/", json=set_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["weight"] == set_data["weight"]
    assert data["repetitions"] == set_data["repetitions"]
    assert "id" in data

def test_update_set(client, auth_headers, create_set, create_exercise):
    exercise_id = create_exercise
    set_id = create_set
    update_set_data = {"weight": 65.0, "repetitions": 10}
    response = client.put(f"/exercises/{exercise_id}/sets/{set_id}", json=update_set_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == set_id
    assert data["weight"] == update_set_data["weight"]
    assert data["repetitions"] == update_set_data["repetitions"]

def test_delete_set(client, auth_headers, create_set, create_exercise):
    exercise_id = create_exercise
    set_id = create_set
    response = client.delete(f"/exercises/{exercise_id}/sets/{set_id}", headers=auth_headers)
    assert response.status_code == 204

    # Проверяем, что подход удален
    get_exercise_response = client.get(f"/exercises/{exercise_id}", headers=auth_headers)
    assert get_exercise_response.status_code == 200
    exercise = get_exercise_response.json()
    assert all(s["id"] != set_id for s in exercise["sets"])

