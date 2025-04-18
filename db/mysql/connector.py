
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

class MySQLConnector:
    def __init__(self, user, password, host, port, database):
        self.url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        try:
            self.engine = create_engine(self.url, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            print("✅ MySQL connecté avec succès.")
        except SQLAlchemyError as e:
            print(f"❌ Erreur de connexion MySQL : {e}")

    def get_session(self):
        if not self.SessionLocal:
            raise Exception("Connexion non établie.")
        return self.SessionLocal()
