import random
import datetime
import jwt
from config import Config


def get_token(role, username):
    payload = {'function': 'usertoken', 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'role': [i.id for i in role], 'username': username, 'random': random.randrange(1000000000, 9999999999)}
    token = str(jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256'), encoding="utf-8")
    return token


def update_token(token):
    payload = jwt.decode(token, Config.SECRET_KEY, algorithms='HS256')
    payload["random"] = random.randrange(1000000000, 9999999999)
    token = str(jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256'), encoding="utf-8")
    return token
