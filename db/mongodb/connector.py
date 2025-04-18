# db/mongodb/connector.py

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoDBConnector:
    def __init__(self, user=None, password=None, host="localhost", port=27018, dbname="easyloc"):
        if user and password:
            uri = f"mongodb://{user}:{password}@{host}:{port}/{dbname}"
        else:
            uri = f"mongodb://{host}:{port}"
        self.client = MongoClient(uri)
        self.db = self.client[dbname]

    def test_connection(self):
        try:
            self.client.admin.command('ping')
            print("✅ MongoDB connecté avec succès.")
        except ConnectionFailure as e:
            print(f"❌ Échec de connexion MongoDB : {e}")
