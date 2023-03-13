import hmac
import hashlib
import base64

from typing import Optional

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response


app = FastAPI()

users = {
    'alexey@user.com': {
        "name": "Алексей",
        "password": "some_password_1",
        "balance": 100_000
    },
    'petr@user.com': {
        "name": "Петр",
        "password": "some_password_2",
        "balance": 555_555
    },
    'alexandra_betsko@user.com': {
        "name": "Александра",
        "password": "some_password_2",
        "balance": 1_000_000
    }
}

SECRET_KEY = "c727ed77f2fd8ddbc99646dfd62420c241319506b56acad4e9c7cd5b0a35e644"


def signed_data(data: str) -> str:
    """Возвращает подписанные данные data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest().upper()


@app.get("/")
def index_page(
    username: Optional[str] = Cookie(default=None)  # Если куки не установлены то Cookie == None
    ):
    """A main site's page"""
    
    with open('templates/login.html', 'r') as f:
        html_login_page = f.read()
    
    if username:  # Если куки есть!
        try:
            user = users[username]
        except KeyError:
            response = Response(html_login_page, media_type='text/html')
            response.delete_cookie(key="username")
            return response
        return Response(
            f"Привет, {users[username]['name']}!",  # То приветствуем пользователя!
            media_type='text/html',
            )
    return Response(
        html_login_page,  # А в противном случае вернем страницу аутентифиции
        media_type="text/html",
    )
    



@app.post("/login")
def process_login_page(
    username : str = Form(...), 
    password : str = Form(...),
    ):
    user = users.get(username)  # Пробуем получить такого пользователя из БД, если такого ключа нет, .get() вернет None
    if not user or user["password"] != password:  # Если user == None или если пароль "user'а из БД" не соответствует введенному 
        return Response(  # То вернуть сообщение -> "Я вас не знаю!"
            'Я вас не знаю!',
            media_type="text/html",
        )
    response = Response(  # Иначе, авторизовать пользователя и поприветствовать нашего красавчика!
        f"Привет, {user['name']}!<br /> Баланс: {user['balance']}",
        media_type="text/html",     
    )
    response.set_cookie(key="username", value=username)
    return response
