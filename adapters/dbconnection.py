from pymongo import MongoClient


class MyMongoDB:
    """
    Classe de conexao Mongo padrao WEB
    """
    def __init__(self):
        self.client = MongoClient('0.0.0.0', 27018)
        self.db = self.client.boticario
        self.dealer_coll = self.db.dealers
        self.sale_coll = self.db.sales

    def get_collection(self, collection):
        if collection == 'dealer':
            return self.dealer_coll
        elif collection == 'sale':
            return self.sale_coll
        else:
            return None

    def insert(self, parameters, collection):
        collection = self.get_collection(collection)
        response = collection.insert_one(parameters)
        return response

    def find_one(self, parameters, collection):
        collection = self.get_collection(collection)
        response = collection.find_one(parameters)
        return response

    def find_all(self, parameters, collection):
        collection = self.get_collection(collection)
        response = collection.find(parameters)
        return response

    def find_one_and_delete(self, parameters, collection):
        collection = self.get_collection(collection)
        response = collection.find_one_and_delete(parameters)
        return response

    def update_one(self, query, campos_put, collection):
        collection = self.get_collection(collection)
        response = collection.update_one(query, {'$set': campos_put})
        return response

