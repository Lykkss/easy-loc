# test/test_mongo_connector.py

from db.mongo.connector import MongoConnector

def main():
    connector = MongoConnector()
    if connector.test_connection():
        print("✅ Connexion MongoDB réussie !")
        print("📂 Collections :", connector.db.list_collection_names())
    else:
        print("❌ Échec de la connexion à MongoDB")

if __name__ == "__main__":
    main()
