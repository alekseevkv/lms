from http import HTTPStatus

import pytest


class TestAuth:
    MSG_8 = "не менее 8 символов"
    MSG_latin = "хотя бы одну заглавную латинскую букву"
    MSG_NUMBER = "хотя бы одну цифру"
    MSG_SPECIAL = "хотя бы один специальный символ"

    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {"payload": {"email": "user@example.com", "password": "string"}},
                {
                    "status": HTTPStatus.UNPROCESSABLE_CONTENT,
                    "msg": f"Value error, Пароль должен содержать: {MSG_8}, {MSG_latin}, {MSG_NUMBER}, {MSG_SPECIAL}",
                },
            ),
            (
                {"payload": {"email": "user@example.com", "password": "stringqwerty"}},
                {
                    "status": HTTPStatus.UNPROCESSABLE_CONTENT,
                    "msg": f"Value error, Пароль должен содержать: {MSG_latin}, {MSG_NUMBER}, {MSG_SPECIAL}",
                },
            ),
            (
                {"payload": {"email": "user@example.com", "password": "stringQwerty"}},
                {
                    "status": HTTPStatus.UNPROCESSABLE_CONTENT,
                    "msg": f"Value error, Пароль должен содержать: {MSG_NUMBER}, {MSG_SPECIAL}",
                },
            ),
            (
                {"payload": {"email": "user@example.com", "password": "stringQwerty1"}},
                {
                    "status": HTTPStatus.UNPROCESSABLE_CONTENT,
                    "msg": f"Value error, Пароль должен содержать: {MSG_SPECIAL}",
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_signup_error(self, query_data, expected_data, aiohttp_client):
        """Тесты /api/v1/auth/signup: регистрация пользователя; проверка некорректных условий"""
        req_url = "/api/v1/auth/signup"

        response = await aiohttp_client.post(req_url, json=query_data["payload"])

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()
            assert content["detail"][0]["msg"] == expected_data["msg"]


    @pytest.mark.asyncio
    async def test_signup(self, aiohttp_client, async_session):
        """Тест /api/v1/auth/signup: регистрация пользователя"""

        req_url = "/api/v1/auth/signup"
        payload = {"email": "user@example.com", "password": "stringQwerty1!"}
        response = await aiohttp_client.post(req_url, json=payload)

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["email"] == payload["email"]

        await async_session.commit() #Для очистки таблицы после теста


    @pytest.mark.asyncio
    async def test_signup_return(self, aiohttp_client, async_session):
        """Тест /api/v1/auth/signup: повторная регистрация пользователя"""

        req_url = "/api/v1/auth/signup"
        payload = {"email": "user@example.com", "password": "stringQwerty1!"}
        await aiohttp_client.post(req_url, json=payload)

        response = await aiohttp_client.post(req_url, json=payload)

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert content["detail"] == "User already exists"

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_signup_admin(self, aiohttp_client, async_session):
        """Тест /api/v1/auth/signup-admin: регистрация админа"""

        req_url = "/api/v1/auth/signup"
        payload = {"email": "admin@example.com", "password": "stringQwerty1!"}
        response = await aiohttp_client.post(req_url, json=payload)

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["email"] == payload["email"]

        await async_session.commit()  # Для очистки таблицы после теста


    @pytest.mark.asyncio
    async def test_signup_return_admin(self, aiohttp_client, async_session):
        """Тест /api/v1/auth/signup-admin: повторная регистрация админа"""

        req_url = "/api/v1/auth/signup-admin"
        payload = {"email": "admin@example.com", "password": "stringQwerty1!"}
        await aiohttp_client.post(req_url, json=payload)

        response = await aiohttp_client.post(req_url, json=payload)

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert content["detail"] == "User already exists"

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_signin(self, aiohttp_client, async_session):
        """Тест /api/v1/auth/signin: вход для пользователя"""
        req_url = "/api/v1/auth/signup"
        payload = {"email": "user@example.com", "password": "stringQwerty1!"}
        await aiohttp_client.post(req_url, json=payload)

        req_url = "/api/v1/auth/signin"
        response = await aiohttp_client.post(req_url, json=payload)

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["token_type"] == "bearer"

        await async_session.commit()


    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {
                    "payload": {"email": "user@example.com", "password": "stringQwerty1!"},
                    "payload_incorrect": {"email": "user_not@example.com", "password": "stringQwerty1!"}
                },
                {
                    "status": HTTPStatus.UNAUTHORIZED,
                    "detail": "Incorrect username or password",
                },
            ),
            (
                {
                    "payload": {"email": "user@example.com", "password": "stringQwerty1!"},
                    "payload_incorrect": {"email": "user@example.com", "password": "stringQwerty1!123"}
                },
                {
                    "status": HTTPStatus.UNAUTHORIZED,
                    "detail": "Incorrect username or password",
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_signin_incorrect(self, query_data, expected_data, aiohttp_client, async_session):
        """Тест /api/v1/auth/signin: неверный пароль"""
        req_url = "/api/v1/auth/signup"
        await aiohttp_client.post(req_url, json=query_data["payload"])

        req_url = "/api/v1/auth/signin"
        response = await aiohttp_client.post(req_url, json=query_data["payload_incorrect"])

        assert response.status == HTTPStatus.UNAUTHORIZED

        if response.status == expected_data["status"]:
            content = await response.json()
            assert content["detail"] == expected_data["detail"]

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_refresh(self, aiohttp_client, async_session, access_token):
        """Тест /api/v1/auth/refresh: обновление токена"""
        token = access_token

        req_url = "/api/v1/auth/refresh"
        response = await aiohttp_client.post(req_url, json={"refresh_token": token["refresh_token"]})

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["token_type"] == "bearer"

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_refresh_error(self, aiohttp_client, async_session, access_token):
        """Тест /api/v1/auth/refresh: передан неверный refresh_token"""

        req_url = "/api/v1/auth/refresh"
        response = await aiohttp_client.post(req_url, json={"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cC"})

        assert response.status == HTTPStatus.UNAUTHORIZED

        if response.status == HTTPStatus.UNAUTHORIZED:
            content = await response.json()
            assert content["detail"] == "Invalid or expired refresh token"

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_logout(self, aiohttp_client, async_session, access_token):
        """Тест /api/v1/auth/logout: корректный выход"""
        token = access_token

        req_url = "/api/v1/auth/logout"
        response = await aiohttp_client.get(req_url, headers={"Authorization": f"Bearer {token["access_token"]}"})

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["msg"] == "OK"

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_logout_error(self, aiohttp_client):
        """Тест /api/v1/auth/logout: пользователь не авторизован"""

        req_url = "/api/v1/auth/logout"
        response = await aiohttp_client.get(req_url)

        assert response.status == HTTPStatus.FORBIDDEN

        if response.status == HTTPStatus.FORBIDDEN:
            content = await response.json()
            assert content["detail"] == "Not authenticated"


    @pytest.mark.asyncio
    async def test_me(self, aiohttp_client, access_token, user_payload, async_session):
        """Тест /api/v1/auth/users/me: пользователь авторизован"""
        token = access_token

        req_url = "/api/v1/auth/users/me"
        response = await aiohttp_client.get(
            req_url, headers={"Authorization": f"Bearer {token['access_token']}"}
        )

        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["email"] == user_payload["email"]

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_me_error(self, aiohttp_client):
        """Тест /api/v1/auth/users/me: пользователь не авторизован"""

        req_url = "/api/v1/auth/users/me"
        response = await aiohttp_client.get(req_url)

        assert response.status == HTTPStatus.FORBIDDEN

        if response.status == HTTPStatus.FORBIDDEN:
            content = await response.json()
            assert content["detail"] == "Not authenticated"


    @pytest.mark.asyncio
    async def test_change_password(self, aiohttp_client, access_token, user_payload, async_session):
        """Тест /api/v1/auth/change-password: корректная смена пароля """
        token = access_token
        req_url = "/api/v1/auth/change-password"

        payload = {
          "old_password": user_payload["password"],
          "new_password": "1stringQwerty1!",
          "new_password_confirm": "1stringQwerty1!"
        }
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["msg"] == "Password changed successfully"

        await async_session.commit()


    @pytest.mark.asyncio
    async def test_change_password_error_password(
        self, aiohttp_client, access_token, user_payload, async_session
    ):
        """Тест /api/v1/auth/change-password: неверный пароль пользователя"""
        token = access_token
        req_url = "/api/v1/auth/change-password"

        payload = {
            "old_password": "ewsFdcnie!d2u1",
            "new_password": "1stringQwerty1!",
            "new_password_confirm": "1stringQwerty1!",
        }
        response = await aiohttp_client.post(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == HTTPStatus.BAD_REQUEST

        if response.status == HTTPStatus.BAD_REQUEST:
            content = await response.json()
            assert content["detail"] == "Current password is incorrect"

        await async_session.commit()


    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {
                    "payload": {
                        "old_password": "1stringQwerty1!",
                        "new_password": "1stringQwerty1",
                        "new_password_confirm": "1stringQwerty1",
                    },
                },
                {
                    "status": HTTPStatus.UNPROCESSABLE_CONTENT,
                    "msg": f"Value error, Пароль должен содержать: {MSG_SPECIAL}",
                },
            ),
            (
                {
                    "payload": {
                        "old_password": "1stringQwerty1!",
                        "new_password": "1stringQwerty1!",
                        "new_password_confirm": "1stringQwerty12ed",
                    },
                },
                {
                    "status": HTTPStatus.UNPROCESSABLE_CONTENT,
                    "msg": "Value error, New passwords don't match",
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_change_password_error_new_password(
        self, query_data, expected_data, aiohttp_client, access_token, user_payload, async_session
    ):
        """Тест /api/v1/auth/change-password: неверные данные паролей"""

        token = access_token
        req_url = "/api/v1/auth/change-password"

        response = await aiohttp_client.post(
            req_url,
            json=query_data["payload"],
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()
            assert content["detail"][0]["msg"] == expected_data["msg"]

        await async_session.commit()

    @pytest.mark.asyncio
    async def test_users(
        self, aiohttp_client, access_token, user_payload, async_session
    ):
        """Тест /api/v1/auth/users: корректное обновление пользователя"""
        token = access_token
        req_url = "/api/v1/auth/users"

        payload = {
            "email": "user_update@example.com",
            "username": "user_name"
        }
        response = await aiohttp_client.patch(
            req_url,
            json=payload,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert response.status == HTTPStatus.OK

        if response.status == HTTPStatus.OK:
            content = await response.json()
            assert content["email"] == payload["email"]

        await async_session.commit()

    @pytest.mark.asyncio
    async def test_users_error(
        self, aiohttp_client, access_token, user_payload, async_session
    ):
        """Тест /api/v1/auth/users: некорректный email"""
        token = access_token
        req_url = "/api/v1/auth/users"

        response = await aiohttp_client.patch(
            req_url,
            json={"email": ""},
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert response.status == HTTPStatus.UNPROCESSABLE_CONTENT

        if response.status == HTTPStatus.UNPROCESSABLE_CONTENT:
            content = await response.json()
            assert (
                content["detail"][0]["msg"]
                == "value is not a valid email address: An email address must have an @-sign."
            )

        await async_session.commit()

    @pytest.mark.asyncio
    async def test_user_double(
        self, aiohttp_client, access_token, user_payload, async_session
    ):
        """Тест /api/v1/auth/users: смена на уже существующий email"""
        req_url = "/api/v1/auth/signup"
        payload = {"email": "user_2@example.com", "password": "stringQwerty1!"}
        await aiohttp_client.post(req_url, json=payload)
        token = access_token
        req_url = "/api/v1/auth/users"

        response = await aiohttp_client.patch(
            req_url,
            json={"email": "user_2@example.com"},
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert response.status == HTTPStatus.CONFLICT
        if response.status == HTTPStatus.CONFLICT:
            content = await response.json()
            assert content["detail"] == "Email already exists"


    @pytest.mark.parametrize(
        "query_data, expected_data",
        [
            (
                {
                    "req_url": "/api/v1/auth/change-password",
                    "method": "post",
                },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
            (
                {
                    "req_url": "/api/v1/auth/users",
                    "method": "patch",
                },
                {
                    "status": HTTPStatus.FORBIDDEN,
                    "detail": f"Not authenticated",
                },
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_not_authorization(self, query_data, expected_data, aiohttp_client):
        """Тесты без авторизации"""
        if query_data["method"] == "post":
            response = await aiohttp_client.post(query_data["req_url"], json={})
        elif query_data["method"] == "patch":
            response = await aiohttp_client.patch(query_data["req_url"], json={})

        assert response.status == expected_data["status"]

        if response.status == expected_data["status"]:
            content = await response.json()
            assert content["detail"] == expected_data["detail"]