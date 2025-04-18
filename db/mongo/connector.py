from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoConnector:
    def __init__(self, host: str = "localhost", port: int = 27017, database: str = "easyloc", username: str = None, password: str = None):
        """Initialise la connexion MongoDB avec authentification optionnelle."""
        if username and password:
            # Si un nom d'utilisateur et un mot de passe sont fournis, créez l'URI avec l'authentification.
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        else:
            # Si aucun identifiant n'est fourni, se connecter sans authentification.
            self.client = MongoClient(host, port, serverSelectionTimeoutMS=5000)
        
        self.db = self.client[database]

    def test_connection(self) -> bool:
        """Teste la connexion à MongoDB."""
        try:
            self.client.admin.command("ping")  # Utilise une commande ping pour vérifier la connexion
            return True
        except ConnectionFailure:
            return False

    def get_collection(self, name: str):
        """Retourne une collection MongoDB."""
        return self.db[name]
