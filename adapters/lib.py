from flask import jsonify
import hashlib, binascii, os


class Lib:
    def __init__(self):
        self.valid = False
        self.json_content = {}

    @staticmethod
    def render_http_json(response_code: int, message: str, payload: dict or list, headers=None) -> dict:
        """
        :param response_code: codigo http
        :param message: mensagem
        :param payload: corpo da requisicao
        :param headers: header da requisicao
        :return: json para o usuario
        """
        combined_headers = {
            'Content-Type': 'application/json'
        }

        if headers is not None:
            combined_headers.update(headers)

        return jsonify({
            'payload': payload,
            'status': response_code,
            'message': message,
            'headers': combined_headers
        })

    @staticmethod
    def calcular_cashback(valor: float) -> object:
        """
        :param valor: valor da venda
        :return: valor percentual e range do cashback
        """
        if valor <= 1000:
            cashback_percentual = '10%'
            cashback_indice = 0.1
        elif valor >= 1001 and valor <= 1500:
            cashback_percentual = '15%'
            cashback_indice = 0.15
        else:
            cashback_percentual = '20%'
            cashback_indice = 0.2

        return cashback_percentual, cashback_indice

    def valid_json_load(self, req, obj) -> dict:
        """
        :param req: corpo da requisicao
        :param obj: campos obrigatorios
        :return: mensagem de erro caso exista
        """
        try:
            self.json_content = req.get_json()
            try:
                params = {}
                for item in obj:
                    params[item] = self.json_content[item]
                return {}
            except KeyError as error:
                return self.render_http_json(422, 'Campo {} obrigatorio no JSON'.format(str(error)), {})
        except KeyError:
            self.json_content = {}
            return self.render_http_json(400, ' JSON invalido ', {})

    @staticmethod
    def hash_password(password: str) -> str:
        """
        :param password:
        :return:
        """
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                      salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        """
        :param stored_password: senha banco de dados
        :param provided_password: senha request
        :return: true ou false
        """
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512',
                                      provided_password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')

        return pwdhash == stored_password

