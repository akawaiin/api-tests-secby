import pytest
import requests


class TestAuthentication:
    """Тесты на авторизацию и аутентификацию"""

    def test_login_with_valid_credentials(self, base_url, auth_payload):
        """
        TC-01: Успешный вход с валидными учетными данными (админ)
        Проверка: получение токена, корректная структура ответа
        """
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=auth_payload
        )

        assert response.status_code == 200, f"Ожидался статус 200, получен: {response.status_code}. Response: {response.text}"
        data = response.json()

        assert "access_token" in data, f"Токен не найден в ответе. Ответ: {data}"
        assert "token_type" in data, f"token_type не найден в ответе. Ответ: {data}"

        token = data["access_token"]
        assert len(token) > 0, "Токен пустой"
        assert token.startswith("eyJ"), f"Токен не в формате JWT. Начало токена: {token[:10]}"

        assert "user" in data, f"Данные пользователя не найдены в ответе. Ответ: {data}"
        assert data["user"]["username"] == auth_payload["username"], \
            f"Ожидался username '{auth_payload['username']}', получен: {data['user'].get('username')}"

    def test_send_token_in_headers(self, base_url, get_token):
        """
        TC-02: Отправка токена в заголовках запроса
        Проверка: токен принимается сервером для доступа к защищённому эндпоинту
        """
        headers = {
            "Authorization": f"Bearer {get_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=headers
        )

        assert response.status_code == 200, f"Токен не принят. Ожидался статус 200, получен: {response.status_code}. Response: {response.text}"

    def test_login_with_invalid_password(self, base_url, auth_payload):
        """
        TC-03: Вход с неверным паролем
        Проверка: получение ошибки 401/403
        """
        payload = {
            "username": auth_payload["username"],
            "password": "wrong_password_12345"
        }

        response = requests.post(
            f"{base_url}/api/auth/login",
            json=payload
        )

        assert response.status_code in [401, 403], \
            f"Ожидалась ошибка 401 или 403, получено: {response.status_code}. Response: {response.text}"

    def test_login_with_invalid_username(self, base_url):
        """
        TC-04: Вход с несуществующим username
        Проверка: получение ошибки 401/403
        """
        payload = {
            "username": "nonexistent_user_xyz",
            "password": "any_password"
        }

        response = requests.post(
            f"{base_url}/api/auth/login",
            json=payload
        )

        assert response.status_code in [401, 403], \
            f"Ожидалась ошибка 401 или 403, получено: {response.status_code}. Response: {response.text}"

    def test_login_with_empty_fields(self, base_url):
        """
        TC-05: Вход с пустыми полями username/password
        Проверка: валидация входных данных
        """
        payload = {
            "username": "",
            "password": ""
        }

        response = requests.post(
            f"{base_url}/api/auth/login",
            json=payload
        )

        assert response.status_code in [400, 401, 403], \
            f"Ожидалась ошибка валидации (400/401/403), получено: {response.status_code}. Response: {response.text}"

    def test_login_with_missing_fields(self, base_url):
        """
        TC-06: Вход с отсутствующими полями в теле запроса
        Проверка: валидация структуры запроса
        """
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={}
        )

        assert response.status_code in [400, 422], \
            f"Ожидалась ошибка валидации (400/422), получено: {response.status_code}. Response: {response.text}"