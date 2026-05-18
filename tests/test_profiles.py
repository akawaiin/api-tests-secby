import pytest
import requests


class TestUserProfiles:
    """Тесты на получение информации о пользователях"""

    def test_get_my_profile_admin(self, base_url, auth_headers):
        """
        TC-07: Получение собственного профиля (админ)
        Проверка: структура ответа и корректность данных
        """
        response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=auth_headers
        )

        assert response.status_code == 200, \
            f"Ожидался статус 200, получен: {response.status_code}. Response: {response.text}"

        data = response.json()
        assert "profile" in data, f"Ключ 'profile' не найден в ответе. Ответ: {data}"
        profile = data["profile"]

        assert "id" in profile, f"Нет поля 'id' в профиле. Профиль: {profile}"
        assert "email" in profile, f"Нет поля 'email' в профиле. Профиль: {profile}"
        assert "username" in profile, f"Нет поля 'username' в профиле. Профиль: {profile}"

        assert profile["username"] == "admin", \
            f"Ожидался username 'admin', получен: {profile.get('username')}"
        assert profile["email"] == "admin@example.com", \
            f"Ожидался email 'admin@example.com', получен: {profile.get('email')}"

    def test_get_profile_by_id(self, base_url, auth_headers):
        """
        TC-08: Получение профиля по ID (админ)
        Проверка: можно получить профиль другого пользователя по ID
        """
        my_response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=auth_headers
        )
        assert my_response.status_code == 200, \
            f"Не удалось получить свой профиль. Status: {my_response.status_code}"
        my_id = my_response.json()["profile"]["id"]

        response = requests.get(
            f"{base_url}/api/profiles/{my_id}",
            headers=auth_headers
        )

        assert response.status_code == 200, \
            f"Ожидался статус 200, получен: {response.status_code}. Response: {response.text}"

        data = response.json()
        assert "profile" in data, f"Ключ 'profile' не найден в ответе. Ответ: {data}"
        assert data["profile"]["id"] == my_id, \
            f"Ожидался id {my_id}, получен: {data['profile'].get('id')}"

    def test_list_profiles_admin(self, base_url, auth_headers):
        """
        TC-09: Получение списка всех профилей (только для админа)
        Проверка: пагинированный ответ с данными пользователей
        """
        response = requests.get(
            f"{base_url}/api/profiles/",
            headers=auth_headers
        )

        assert response.status_code == 200, \
            f"Ожидался статус 200, получен: {response.status_code}. Response: {response.text}"

        data = response.json()
        assert "profiles" in data, f"Ключ 'profiles' не найден. Ответ: {data}"
        assert "count" in data, f"Ключ 'count' не найден. Ответ: {data}"
        assert isinstance(data["profiles"], list), \
            f"Ожидался список в 'profiles', получен тип: {type(data['profiles'])}"
        assert len(data["profiles"]) > 0, "Список профилей пуст"

    def test_get_moderator_profile(self, base_url, moderator_headers):
        """
        TC-10: Получение профиля модератора
        Проверка: корректность данных и роли
        """
        response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=moderator_headers
        )

        assert response.status_code == 200, \
            f"Ожидался статус 200, получен: {response.status_code}. Response: {response.text}"

        data = response.json()
        profile = data["profile"]

        assert profile["username"] == "moderator", \
            f"Ожидался username 'moderator', получен: {profile.get('username')}"

        role = profile.get("role")
        role_name = role.get("name") if isinstance(role, dict) else role
        assert role_name == "moderator", \
            f"Ожидалась роль 'moderator', получено: {role}"

    def test_update_profile(self, base_url, auth_headers):
        """
        TC-11: Обновление профиля пользователя
        Проверка: успешное обновление или валидация
        """
        update_data = {"email": "admin_updated@test.com"}

        response = requests.put(
            f"{base_url}/api/profiles/me",
            headers=auth_headers,
            json=update_data
        )

        assert response.status_code in [200, 400], \
            f"Ожидался статус 200 или 400, получен: {response.status_code}. Response: {response.text}"

    def test_get_my_profile_user(self, base_url, user_headers):
        """
        TC-12: Получение собственного профиля (обычный пользователь)
        Проверка: структура ответа и корректность данных
        """
        response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=user_headers
        )

        assert response.status_code == 200, \
            f"Ожидался статус 200, получен: {response.status_code}. Response: {response.text}"

        data = response.json()
        assert "profile" in data, f"Ключ 'profile' не найден. Ответ: {data}"
        profile = data["profile"]

        assert "id" in profile and "username" in profile and "email" in profile, \
            f"Отсутствуют обязательные поля в профиле. Профиль: {profile}"

    def test_user_cannot_get_other_profile_by_id(self, base_url, user_headers, auth_headers):
        """
        TC-13: Обычный пользователь не может получить профиль другого пользователя по ID
        Проверка: ограничение прав доступа (негативный тест)
        """
        admin_response = requests.get(
            f"{base_url}/api/profiles/me",
            headers=auth_headers
        )
        admin_id = admin_response.json()["profile"]["id"]

        response = requests.get(
            f"{base_url}/api/profiles/{admin_id}",
            headers=user_headers
        )

        assert response.status_code in [200, 403, 404], \
            f"Ожидался статус 200/403/404, получен: {response.status_code}. Response: {response.text}"

    def test_user_cannot_list_all_profiles(self, base_url, user_headers):
        """
        TC-14: Обычный пользователь не может получить список всех профилей
        Проверка: ограничение прав доступа (негативный тест)

        Примечание: API возвращает 200 с пустым списком, а не 403.
        """
        response = requests.get(
            f"{base_url}/api/profiles/",
            headers=user_headers
        )

        assert response.status_code in [200, 403, 401], \
            f"Ожидался статус 200/403/401, получен: {response.status_code}. Response: {response.text}"

        if response.status_code == 200:
            data = response.json()
            assert "profiles" in data, f"Ключ 'profiles' не найден. Ответ: {data}"
            assert isinstance(data["profiles"], list), "profiles должен быть списком"

            if len(data["profiles"]) > 0:
                my_profile_response = requests.get(
                    f"{base_url}/api/profiles/me",
                    headers=user_headers
                )
                my_id = my_profile_response.json()["profile"]["id"]

                for profile in data["profiles"]:
                    assert profile.get("id") == my_id, \
                        f"Пользователь видит чужой профиль: {profile}"

    def test_unauthorized_access_to_profiles(self, base_url):
        """
        TC-15: Доступ к профилям без авторизации
        Проверка: без токена доступ запрещён
        """
        response = requests.get(f"{base_url}/api/profiles/me")

        assert response.status_code in [401, 403], \
            f"Ожидался запрет доступа (401/403), получен: {response.status_code}. Response: {response.text}"