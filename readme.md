# Documentation de la Bibliothèque EasyLoc

Ce document présente la bibliothèque de gestion des bases de données d'EasyLoc, qui permet d'interagir avec des bases SQL (MySQL) et NoSQL (MongoDB) pour gérer contrats de location, clients et véhicules.

---

## 1. Introduction

La bibliothèque simplifie l'accès aux données des agences pour les équipes frontend et backend en proposant une API standardisée reposant sur le pattern DAO (Data Access Object).

---

## 2. Architecture du Code

L'architecture suit deux axes principaux :

- **DAO (Data Access Object)** : Chaque entité possède un DAO dédié pour les opérations CRUD.
- **Gestion des connexions** : Une classe spécifique gère la connexion aux bases MongoDB et MySQL.

---

### 2.1 Connexion à MongoDB

La classe `MongoConnector` permet de se connecter à une base MongoDB en utilisant un URI de connexion, avec option d'authentification.

```python
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class MongoConnector:
    def __init__(self, host: str = "localhost", port: int = 27017, database: str = "easyloc", username: str = None, password: str = None):
        """Initialise la connexion MongoDB avec authentification optionnelle."""
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        else:
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
        """Retourne la collection MongoDB spécifiée."""
        return self.db[name]
```

**Fonctionnalités :**
- Connexion sécurisée avec ou sans authentification.
- Méthode pour tester la connexion.
- Accès aux collections via `get_collection`.

---

### 2.2 Connexion à MySQL

La classe `MySQLConnector` s'occupe de la connexion MySQL via le module `mysql.connector`.

```python
import mysql.connector

class MySQLConnector:
    def __init__(self, host: str, user: str, password: str, database: str):
        """Initialise la connexion MySQL."""
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def test_connection(self) -> bool:
        """Teste la connexion à MySQL."""
        try:
            self.cursor.execute("SELECT 1")
            return True
        except mysql.connector.Error:
            return False

    def get_cursor(self):
        """Retourne le curseur pour exécuter des requêtes SQL."""
        return self.cursor
```

**Fonctionnalités :**
- Connexion sécurisée à MySQL.
- Test de connexion via une requête simple.
- Accès au curseur pour l'exécution de requêtes.

---

### 2.3 Les DAOs

Les DAO (Data Access Objects) gèrent les opérations CRUD sur les entités. Les principaux DAO sont :

- **CustomerDAO** : Gère les opérations sur la collection Customer (MongoDB).
- **VehicleDAO** : Gère les opérations sur la collection Vehicle (MongoDB).
- **ContractDAO** : Gère les opérations sur la table Contract (MySQL).
- **BillingDAO** : Gère les opérations sur la table Billing (MySQL).

#### Exemple - CustomerDAO

```python
class CustomerDAO:
    def __init__(self, connector: MongoConnector):
        self.collection = connector.get_collection('Customer')

    def create_customer(self, customer: dict):
        self.collection.insert_one(customer)

    def get_customer_by_uid(self, uid: str):
        return self.collection.find_one({"uid": uid})
```

**Méthodes typiques :**
- `create_*` : Créer une entité.
- `get_*` : Récupérer une entité par son ID ou critère.
- `update_*` : Mettre à jour une entité.
- `delete_*` : Supprimer une entité.

---

## 3. Documentation des Tests Unitaires

Les tests unitaires, écrits avec pytest, vérifient le bon fonctionnement de la bibliothèque.

### 3.1 Tests de Connexion

- **MongoDB** : Test de connexion avec et sans authentification.
- **MySQL** : Test de connexion via une simple requête.

### 3.2 Tests des Opérations CRUD

Les tests vérifient la création, la lecture, la mise à jour et la suppression des entités.  
Par exemple :

#### Exemple de test pour CustomerDAO

```python
import uuid

def test_create_and_get_customer(dao):
    uid = str(uuid.uuid4())
    customer = {
        "uid": uid,
        "first_name": "Alice",
        "second_name": "Martin",
        "address": "1 rue des tests",
        "permit_number": "PERM5678"
    }
    dao.create_customer(customer)
    fetched = dao.get_customer_by_uid(uid)
    assert fetched is not None
    assert fetched["first_name"] == "Alice"
```

---

## 4. Choix d'Architecture

### 4.1 Gestion des Bases de Données

- **MongoDB** est utilisé pour les données moins structurées (Customer, Vehicle).
- **MySQL** est préféré pour les données transactionnelles et les contraintes de schéma (Contract, Billing).

### 4.2 Architecture Modulaire

Chaque composant (connexion ou DAO) est indépendant, facilitant ainsi l'ajout de nouveaux SGBD ou de nouvelles entités.

### 4.3 Sécurité

- **Validation des entrées** : Prévention des injections SQL/NoSQL.
- **Authentification** : Mécanismes sécurisés pour les connexions aux bases de données.

---

## 5. Installation et Utilisation

### 5.1 Prérequis

- Python 3.11
- pytest pour les tests
- Docker et docker-compose pour l'environnement des bases de données

### 5.2 Installation

1. Cloner le dépôt :
   ```
   git clone https://github.com/Lykkss/easy-loc.git
   cd easy-loc
   ```
2. Créer et activer un environnement virtuel :
   ```
   conda create --name easyloc_env python=3.11
   conda activate easyloc_env
   ```
3. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```
4. Démarrer les containers Docker :
   ```
   cd docker
   docker-compose up --build -d
   ```

### 5.3 Lancer les Tests

Exécuter tous les tests avec :
```
pytest tests/ --maxfail=1 --disable-warnings -v
```

---

## 6. Conclusion

La bibliothèque EasyLoc offre une solution complète pour gérer les bases de données via une architecture modulaire et sécurisée. Elle est facilement extensible pour intégrer de nouvelles fonctionnalités ou SGBD.

N'hésitez pas à adapter cette documentation en fonction de vos besoins, en ajoutant des liens ou des détails spécifiques au projet.






