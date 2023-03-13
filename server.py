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
        "password": "a5145a42b4915e808673dd5664fd90de17f3645f58cfbce0cc5d679a827cef1e",
        "balance": 100_000
    },
    'petr@user.com': {
        "name": "Петр",
        "password": "bca84553457b14249cd577f0de4b46ab6502eb63d6dee3bccbf221c29b5d9b96",
        "balance": 555_555
    },
    'alexandra_betsko@user.com': {
        "name": "Александра",
        "password": "7b9a361f8584da99cb0ed17c3205ff645738bb0a3c8135ad32818263865e9b93",
        "balance": 1_000_000
    }
}

SECRET_KEY = "c727ed77f2fd8ddbc99646dfd62420c241319506b56acad4e9c7cd5b0a35e644"
PASSWORD_SALT = "2936c7701d34684b1f6caefc7bcffd5a76e8d8ff31d99c6b7ddd3cb3e5e6a79c"

def verify_password(username: str, password: str) -> bool:
    password_hash = hashlib.sha256( (password + PASSWORD_SALT).encode() ).hexdigest().lower()
    stored_password_hash = users[username]["password"].lower()
    return password_hash == stored_password_hash



def signed_data(data: str) -> str:
    """Возвращает подписанные данные data"""
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest().upper()
    

def get_username_from_signed_string(username_signed: str) -> Optional[str]: 
    """Возвращает обычный username от шифрованной"""
    username_base64, sign = username_signed.split(".")  # Разобьем строку
    username = base64.b64decode(username_base64.encode()).decode()  # Декодируем base64
    valid_sign = signed_data(username)  # Получаем валидную подпись 
    if hmac.compare_digest(valid_sign, sign):  # Сравниваем валидную подпись с тем что пришло (ожидаем одинаковые данные)
        return username  # Если пришли валидные данные - вернуть обычную строку
    # Иначе, ничего не возвращаем

@app.get("/")
def index_page(
    username: Optional[str] = Cookie(default=None)  # Если куки не установлены то Cookie == None
    ):
    """A main site's page"""
    
    with open('templates/login.html', 'r') as f:
        html_login_page = f.read()
    
    if not username:  # Если в куку ничего не прилетело!
        return Response(
        html_login_page, # То вернем пользователя на начальную страницу
        media_type="text/html",
    )
    # Иначе если (проверка на валидный юзернейм)...
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(html_login_page, media_type='text/html')  # Если нет
        response.delete_cookie(key="username")                        # Удаляем куки
        return response                                               # Возвращаем на начальную страницу
    # Иначе если юзернейм валидный
    try:  # В случае если нет или есть такой пользователь в нашем словаре
        user = users[valid_username]
    except KeyError:
        response = Response(html_login_page, media_type='text/html')  # Если нет
        response.delete_cookie(key="username")                        # Удаляем куки
        return response                                               # Возвращаем на начальную страницу
    # Но если есть такой пользователь
    return Response(
        f"Привет, {users[valid_username]['name']}!",  # То приветствуем пользователя!
        media_type='text/html',
        )



@app.post("/login")
def process_login_page(
    username : str = Form(...), 
    password : str = Form(...),
    ):
    user = users.get(username)  # Пробуем получить такого пользователя из БД, если такого ключа нет, .get() вернет None
    if not user or not verify_password(username, password):  # Если user == None или если не verify_password(username, password)
        return Response(  # То вернуть сообщение -> "Я вас не знаю!"
            'Я вас не знаю!',
            media_type="text/html",
        )
    response = Response(  # Иначе, авторизовать пользователя и поприветствовать нашего красавчика!
        f"Привет, {user['name']}!<br /> Баланс: {user['balance']}",
        media_type="text/html",     
    )
    username_signed = base64.b64encode(username.encode()).decode() + "." + signed_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response
