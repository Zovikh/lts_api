import pytest
import requests


class TestUserAuth:
    def test_auth_user(self):
        data = {
            "email": "vinkotov@example.com",
            "password": "1234"
        }
        # отправляем POST-запрос на логин
        # Проверяем, что сервер вернул cookie-сессию, CSRF-токен и user_id
        response1 = requests.post("https://playground.learnqa.ru/api/user/login", data = data)

        # Проверяем, что в ответе есть cookie auth_sid, сессия создана
        assert "auth_sid" in response1.cookies, "There is no auth cookie in the response"
        # Проверяем, что в заголовках есть x-csrf-token нужен для защиты от CSRF-атак
        assert "x-csrf-token" in response1.headers, "There is no CSRF token header in the response"
        # Проверяем, что в JSON-ответе есть user_id, сервер распознал пользователя
        assert "user_id" in response1.json(), "There is no user id in the response"

        # Извлекаем значения для повторной проверки авторизации
        auth_sid = response1.cookies.get("auth_sid") # идентификатор сессии
        token = response1.headers.get("x-csrf-token") # CSRF-токен из заголовка
        user_id_from_auth_method = response1.json()["user_id"] # user_id из первого ответа

        # отправляем GET-запрос на /api/user/auth
        # Передаём те же cookie и токен, что получили при логине
        # проверяем, что сервер узнаёт пользователя по сессии
        response2 = requests.get(
        "https://playground.learnqa.ru/api/user/auth",
            headers = {"x-csrf-token": token},
            cookies = {"auth_sid": auth_sid}
        )

        # Проверяем, что второй ответ тоже содержит user_id
        assert "user_id" in response2.json(), "There is no user id in the second response"
        user_id_from_check_method = response2.json()["user_id"]

        # основная проверка. user_id из логина должен совпадать с user_id из проверки авторизации
        # Если они разные сессия не сохранилась или передаётся неправильно
        assert user_id_from_auth_method == user_id_from_check_method, \
            "User id from auth method is not equal to user id from check method"

    exclude_params = [
        ("no_cookie"),
        ("no_token")
    ]

    @pytest.mark.parametrize('condition', exclude_params)
    def test_negative_auth_check(self, condition):
        data = {
            "email": "vinkotov@example.com",
            "password": "1234"
        }

        response1 = requests.post("https://playground.learnqa.ru/api/user/login", data=data)

        assert "auth_sid" in response1.cookies, "There is no auth cookie in the response"
        assert "x-csrf-token" in response1.headers, "There is no CSRF token header in the response"
        assert "user_id" in response1.json(), "There is no user id in the response"

        auth_sid = response1.cookies.get("auth_sid")
        token = response1.headers.get("x-csrf-token")

        if condition == "no_cookie":
            response2 = requests.get(
                "https://playground.learnqa.ru/api/user/auth",
                headers = {"x-csrf-token": token}
            )
        else:
            response2 = requests.get(
                "https://playground.learnqa.ru/api/user/auth",
                cookies = {"auth_sid": auth_sid}
            )

        assert "user_id" in response1.json(), "There is no user id in the second response"

        user_id_from_check_method = response2.json()["user_id"]

        assert user_id_from_check_method == 0, f"User is authorized with condition {condition}"

