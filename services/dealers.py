from adapters.dbconnection import MyMongoDB
from adapters.lib import Lib
from services.auth import gerar_jwt


class DealersServices:
    def __init__(self):
        self.lib = Lib()
        self.db = MyMongoDB()
        self.resp = {}

    def get_dealers(self) -> dict:
        """

        :return: mensagem json
        """
        dealers = []
        for dealer in self.db.find_all({}, 'dealer'):
            dealer['_id'] = str(dealer['_id'])
            dealers.append(dealer)
        return self.lib.render_http_json(200, 'Solicitação bem-sucedida', dealers)

    def valid_dealer(self, params: dict) -> dict:
        """
        :param params: request requisicao
        :return: mensagem json
        """
        data = self.db.find_one({'cpf': params['cpf']}, 'dealer')
        if not data:
            self.resp['http_code'] = 401
            self.resp['message'] = 'Cpf nao encontrado'
            self.resp['payload'] = {}
        else:
            if self.lib.verify_password(data['senha'], params['senha']):
                self.resp['http_code'] = 200
                self.resp['message'] = 'Solicitação bem-sucedida'
                self.resp['payload'] = {'authorization': gerar_jwt(params['cpf'])}
            else:
                self.resp['http_code'] = 401
                self.resp['message'] = 'Senha incorreta'
                self.resp['payload'] = {}

        return self.lib.render_http_json(self.resp['http_code'], self.resp['message'], self.resp['payload'])

    def create_dealer(self, params: dict) -> dict:
        """
        :param params: request requisicao
        :return: mensagem json
        """
        if self.db.find_one({'cpf': params['cpf']}, 'dealer'):
            self.resp['http_code'] = 409
            self.resp['message'] = 'Cpf ja cadastrado'
        else:
            params['senha'] = self.lib.hash_password(params['senha'])
            self.db.insert(params, 'dealer')
            self.resp['http_code'] = 200
            self.resp['message'] = 'Revendedor criado com sucesso'
        return self.lib.render_http_json(self.resp['http_code'], self.resp['message'], {})

