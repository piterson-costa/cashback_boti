from adapters.dbconnection import MyMongoDB
from adapters.lib import Lib
from flask import current_app
import requests
import json


class SalesServices:

    def __init__(self):
        self.lib = Lib()
        self.db = MyMongoDB()
        self.resp = {}

    def get_sales(self) -> dict:
        """
        :return: mensagem json
        """
        sale_list = []
        for sale in self.db.find_all({}, 'sale'):
            sale['_id'] = str(sale['_id'])
            porcentagem, indice = self.lib.calcular_cashback(float(sale['valor']))
            sale['cashback_porcentagem'] = porcentagem
            sale['cashback_valor'] = round((float(sale['valor']) * float(indice)), 2)
            sale_list.append(sale)

        return self.lib.render_http_json(200, 'Solicitação bem-sucedida', sale_list)

    def create_sale(self, params: dict) -> dict:
        """
        :param params: request requisicao
        :return: mensagem json
        """
        if self.db.find_one({'codigo': params['codigo']}, 'sale'):
            self.resp['http_code'] = 409
            self.resp['message'] = 'nao foi possivel cadastrar a compra, codigo ja existente'
        else:
            params['status'] = 'Em validação' if params['venda_cpf'] != '15350946056' else 'Aprovado'
            params['valor'] = float(params['valor'])
            self.db.insert(params, 'sale')
            self.resp['http_code'] = 200
            self.resp['message'] = 'Venda cadastrada com sucesso!'

        return self.lib.render_http_json(self.resp['http_code'], self.resp['message'], {})

    def update_sale(self, params: dict) -> dict:
        """
        :param params: request requisicao
        :return: mensagem json
        """
        query = {'venda_cpf': params['venda_cpf'], 'codigo': params['codigo']}
        status_check = self.db.find_one(query, 'sale')
        if status_check:
            if status_check['status'] != 'Aprovado':
                put_list = {}
                for key, value in params['campos_put'].items():
                    if value:
                        put_list[key] = value
                campos_put = put_list
                self.db.update_one(query, campos_put, 'sale')
                self.resp['http_code'] = 200
                self.resp['message'] = 'Venda atualizada com sucesso'
            else:
                self.resp['http_code'] = 400
                self.resp['message'] = 'Status da venda ja esta aprovado'
        else:
            self.resp['http_code'] = 400
            self.resp['message'] = 'Item nao encontrado'

        return self.lib.render_http_json(self.resp['http_code'], self.resp['message'], {})

    def delete_sale(self, params: dict) -> dict:
        """
        :param params: request requisicao
        :return: mensagem json
        """

        status_check = self.db.find_one(params, 'sale')
        if status_check:
            if status_check['status'] != 'Aprovado':
                self.db.find_one_and_delete(params, 'sale')
                self.resp['http_code'] = 200
                self.resp['message'] = 'Venda deletada com sucesso'
            else:
                self.resp['http_code'] = 400
                self.resp['message'] = 'Impossivel excluir item, status ja aprovado'
        else:
            self.resp['http_code'] = 400
            self.resp['message'] = 'Item nao encontrado'

        return self.lib.render_http_json(self.resp['http_code'], self.resp['message'], {})

    def get_cashback(self) -> dict:
        """
        :return: mensagem json
        """
        try:
            req = requests.get(current_app.config['URL_API'], headers={'token': current_app.config['SECRET_KEY']})
        except ConnectionError:
            self.resp['http_code'] = 500
            self.resp['message'] = 'Problema ao conectar com a API'
            self.resp['payload'] = {}
            return self.lib.render_http_json(self.resp['http_code'], self.resp['message'], self.resp['payload'])

        http_code = req.status_code
        if http_code != 200:
            self.resp['http_code'] = http_code
            self.resp['message'] = 'Solicitação mal sucedida'
            self.resp['payload'] = {}
        else:
            ret = json.loads(req.text)
            self.resp['http_code'] = 200
            self.resp['message'] = 'Solicitação bem sucedida!'
            self.resp['payload'] = ret['body']

        return self.lib.render_http_json(self.resp['http_code'], self.resp['message'], self.resp['payload'])
