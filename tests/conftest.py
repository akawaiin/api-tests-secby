import pytest
import requests

BASE_URL = "https://secby.ru"

@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def auth_payload():
    """Данные для входа администратора"""
    return {
        "username": "admin",
        "password": "admin123"
    }

@pytest.fixture
def moderator_payload():
    """Данные для входа модератора"""
    return {
        "username": "moderator",
        "password": "moderator123"
    }

@pytest.fixture
def get_token(base_url, auth_payload):
    """Получение токена"""
    response = requests.post(
        f"{base_url}/api/auth/login",
        json=auth_payload
    )
    assert response.status_code == 200, "Не удалось получить токен"
    token = response.json().get("access_token")
    assert token is not None, "Токен не возвращен в ответе"
    return token

@pytest.fixture
def get_moderator_token(base_url, moderator_payload):
    """Получение токена модератора"""
    response = requests.post(
        f"{base_url}/api/auth/login",
        json=moderator_payload
    )
    assert response.status_code == 200, "Не удалось получить токен модератора"
    token = response.json().get("access_token")
    assert token is not None, "Токен модератора не возвращен"
    return token

@pytest.fixture
def auth_headers(get_token):
    """Заголовки с токеном авторизации"""
    return {
        "Authorization": f"Bearer {get_token}",
        "Content-Type": "application/json"
    }