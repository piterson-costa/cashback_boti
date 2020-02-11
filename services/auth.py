from adapters.dbconnection import MyMongoDB
from adapters.lib import Lib
from flask import request, current_app
from functools import wraps
import jwt
import datetime

mongo = MyMongoDB()
lib = Lib()


def gerar_jwt(dealer_cpf: str) -> str:
    """
    :param dealer_cpf: cpf do revendedor
    :return: token jwt
    """
    token_jwt = jwt.encode({
        'dealer': dealer_cpf,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }, current_app.config['SECRET_KEY']).decode("utf-8")

    return token_jwt


def validar_jwt(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        authorization = request.headers.get('authorization')
        if not authorization:
            return lib.render_http_json(401, 'Header authorization obrigatorio', {})
        try:
            data = jwt.decode(authorization, current_app.config['SECRET_KEY'])
            mongo.find_one({'cpf': data['dealer']}, 'dealer')
        except Exception:
            return lib.render_http_json(401, 'Header authorization incorreto!', {})

        return f(*args, **kwargs)

    return wrapper

