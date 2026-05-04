import pytest
import requests


class TestUserProfiles:
    """Тесты на получение информации о пользователях"""

    def test_get_my_profile(self, base_url, auth_headers):
        """
        TC-06: Получение собственного профиля
        """
        response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=auth_headers
        )

        assert response.status_code == 200, f"Status code: {response.status_code}"
        data = response.json()

        assert "profile" in data, "Ключ 'profile' не найден в ответе"
        profile = data["profile"]

        assert "id" in profile, "Нет id в профиле"
        assert "email" in profile, "Нет email в профиле"
        assert "username" in profile or "role" in profile, "Нет username или role в профиле"

    def test_get_profile_by_id(self, base_url, auth_headers):
        """
        TC-07: Получение профиля по ID
        """
        my_response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=auth_headers
        )
        my_id = my_response.json()["profile"]["id"]

        response = requests.get(
            f"{base_url}/api/profiles/{my_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Ответ также содержит профиль в ключе "profile"
        assert "profile" in data
        assert data["profile"]["id"] == my_id

    def test_get_admin_profile(self, base_url, auth_headers):
        """
        TC-08: Получение информации об администраторе
        """
        response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        profile = data["profile"]

        role = profile.get("role")
        role_name = role.get("name") if isinstance(role, dict) else role

        assert role_name == "admin", f"Ожидалась роль admin, получена: {role}"
        assert profile.get("username") == "admin", "Это не аккаунт admin"

    def test_list_profiles_admin(self, base_url, auth_headers):
        """
        TC-09: Получение списка всех профилей (только для админа)
        """
        response = requests.get(
            f"{base_url}/api/profiles/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "profiles" in data, "Ключ 'profiles' не найден"
        assert "count" in data, "Ключ 'count' не найден"
        assert isinstance(data["profiles"], list), "profiles должен быть списком"
        assert len(data["profiles"]) > 0, "Список профилей пуст"

    def test_get_moderator_profile(self, base_url, get_moderator_token):
        """
        TC-10: Получение профиля модератора
        """
        headers = {
            "Authorization": f"Bearer {get_moderator_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        profile = data["profile"]

        role = profile.get("role")
        role_name = role.get("name") if isinstance(role, dict) else role

        assert role_name == "moderator", f"Ожидалась роль moderator, получена: {role}"
        assert profile.get("username") == "moderator"

    def test_update_profile(self, base_url, auth_headers):
        """
        TC-11: Обновление профиля пользователя
        """
        update_data = {"email": "admin_updated@test.com"}

        response = requests.put(
            f"{base_url}/api/profiles/me",
            headers=auth_headers,
            json=update_data
        )

        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"

    def test_unauthorized_access_to_profiles(self, base_url):
        """
        TC-12: Доступ к профилям без авторизации
        """
        response = requests.get(f"{base_url}/api/profiles/me")

        assert response.status_code in [401, 403], f"Без токена должен быть 401/403, получено: {response.status_code}"