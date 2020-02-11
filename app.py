from flask import Flask, request
from adapters.lib import Lib
from services.sales import SalesServices
from services.dealers import DealersServices
from services.auth import validar_jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ZXPURQOARHiMc6Y0flhRC1LVlZQVFRnm'
app.config['URL_API'] = 'https://mdaqk8ek5j.execute-api.us-east-1.amazonaws.com/v1/cashback?cpf=12312312323'

sales_services = SalesServices()
dealer_services = DealersServices()
lib = Lib()


@app.route('/login', methods=['GET'])
def login():
    error = lib.valid_json_load(request, {'cpf', 'senha'})
    if not error:
        return dealer_services.valid_dealer(lib.json_content)
    else:
        return error


@app.route('/dealers', methods=['POST', 'GET'])
def dealers():
    if request.method == 'POST':
        error = lib.valid_json_load(request, {'nome', 'cpf', 'email', 'senha'})
        if not error:
            return dealer_services.create_dealer(lib.json_content)
        else:
            return error
    if request.method == 'GET':
        return dealer_services.get_dealers()


@app.route('/sales', methods=['GET'])
@validar_jwt
def sales():
    return sales_services.get_sales()


@app.route('/sales_delete', methods=['DELETE'])
@validar_jwt
def sales_delete():
    error = lib.valid_json_load(request, {'codigo', 'venda_cpf'})
    if not error:
        return sales_services.delete_sale(lib.json_content)
    else:
        return error


@app.route('/sales_create', methods=['POST'])
@validar_jwt
def sales_create():
    error = lib.valid_json_load(request, {'codigo', 'valor', 'data', 'venda_cpf'})
    if not error:
        return sales_services.create_sale(lib.json_content)
    else:
        return error


@app.route('/sales_update', methods=['PUT'])
@validar_jwt
def sales_update():
    error = lib.valid_json_load(request, {'codigo', 'venda_cpf', 'campos_put'})
    if not error:
        return sales_services.update_sale(lib.json_content)
    else:
        return error


@app.route('/get_cashback', methods=['GET'])
@validar_jwt
def get_cashback():
    return sales_services.get_cashback()


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
