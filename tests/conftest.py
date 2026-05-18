import pytest
import requests

BASE_URL = "https://secby.ru"


@pytest.fixture
def base_url():
    """Базовый URL API"""
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
def user_payload():
    """Данные для входа обычного пользователя"""
    return {
        "username": "user_Malkova_1",
        "password": "SecurePass123!",
        "email": "test_malkova@example.com"
    }


@pytest.fixture
def get_token(base_url, auth_payload):
    """Получение токена администратора"""
    response = requests.post(
        f"{base_url}/api/auth/login",
        json=auth_payload
    )
    assert response.status_code == 200, \
        f"Не удалось получить токен админа. Status: {response.status_code}, Response: {response.text}"
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
    assert response.status_code == 200, \
        f"Не удалось получить токен модератора. Status: {response.status_code}, Response: {response.text}"
    token = response.json().get("access_token")
    assert token is not None, "Токен модератора не возвращен"
    return token


@pytest.fixture
def get_user_token(base_url, user_payload):
    """Получение токена обычного пользователя"""
    # Предполагаем, что пользователь уже зарегистрирован
    response = requests.post(
        f"{base_url}/api/auth/login",
        json=user_payload
    )

    assert response.status_code == 200, \
        f"Не удалось войти как '{user_payload['username']}'. " \
        f"Status: {response.status_code}, Response: {response.text}. " \
        f"Убедитесь, что пользователь зарегистрирован через /api/auth/register"

    token = response.json().get("access_token")
    assert token is not None, "Токен пользователя не возвращен"
    return token


@pytest.fixture
def auth_headers(get_token):
    """Заголовки с токеном авторизации администратора"""
    return {
        "Authorization": f"Bearer {get_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def moderator_headers(get_moderator_token):
    """Заголовки с токеном авторизации модератора"""
    return {
        "Authorization": f"Bearer {get_moderator_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def user_headers(get_user_token):
    """Заголовки с токеном авторизации обычного пользователя"""
    return {
        "Authorization": f"Bearer {get_user_token}",
        "Content-Type": "application/json"
    }