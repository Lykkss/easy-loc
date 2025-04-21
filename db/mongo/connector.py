# db/mongo/connector.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoConnector:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        database: str = "easyloc",
        username: str | None = None,
        password: str | None = None
    ):
        """Initialise la connexion MongoDB avec authentification optionnelle."""
        if username and password:
            # URI avec authentification et authSource=database
            uri = (
                f"mongodb://{username}:{password}@{host}:{port}/{database}"
                f"?authSource={database}"
            )

            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        else:
            # Connexion sans authentification
            self.client = MongoClient(host, port, serverSelectionTimeoutMS=5000)

        self.db = self.client[database]

    def test_connection(self) -> bool:
        """Teste la connexion à MongoDB."""
        try:
            self.client.admin.command("ping")
            return True
        except ConnectionFailure:
            return False

    def get_collection(self, name: str):
        """Retourne une collection MongoDB."""
        return self.db[name]