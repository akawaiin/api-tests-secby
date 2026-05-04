import pytest
import requests


class TestAuthentication:
    """Тесты на авторизацию и аутентификацию"""

    def test_login_with_valid_credentials(self, base_url, auth_payload):
        """
        TC-01: Успешный вход с валидными учетными данными
        """
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=auth_payload
        )

        assert response.status_code == 200, f"Status code: {response.status_code}"
        data = response.json()

        assert "access_token" in data, "Токен не найден в ответе"
        assert "token_type" in data, "token_type не найден"

        token = data["access_token"]
        assert len(token) > 0, "Токен пустой"
        assert token.startswith("eyJ"), "Токен не в формате JWT"

    def test_login_admin_get_token(self, base_url):
        """
        TC-02: Вход как администратор и проверка токена
        """
        payload = {"username": "admin", "password": "admin123"}

        response = requests.post(
            f"{base_url}/api/auth/login",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == "admin"

    def test_send_token_in_headers(self, base_url, get_token):
        """
        TC-03: Отправка токена в заголовках запроса
        """
        headers = {
            "Authorization": f"Bearer {get_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=headers
        )

        assert response.status_code == 200, f"Токен не принят. Status: {response.status_code}"

    def test_login_with_invalid_password(self, base_url):
        """
        TC-04: Вход с неверным паролем
        """
        payload = {"username": "admin", "password": "wrong_password"}

        response = requests.post(
            f"{base_url}/api/auth/login",
            json=payload
        )

        assert response.status_code in [401, 403], f"Ожидалась ошибка, получено: {response.status_code}"

    def test_verify_token(self, base_url, get_token):
        """
        TC-05: Проверка валидности токена
        """
        headers = {
            "Authorization": f"Bearer {get_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{base_url}/api/auth/verify",
            headers=headers
        )

        if response.status_code == 404:
            pytest.skip("Эндпоинт /api/auth/verify не реализован")
        assert response.status_code == 200, "Токен не прошел проверку"