# EasyLoc Data Access Library & API

La bibliothèque **EasyLoc** fournit une couche d’accès aux données pour les services de location de voitures, en combinant :

- **MongoDB** (NoSQL) pour les entités **Customer** et **Vehicle**  
- **MySQL** (SQL) pour les entités **Contract** et **Billing**

Elle expose également une API REST (FastAPI) pour consommer ces données depuis n’importe quel client (frontend, outils CLI, etc.).

---

## Table des matières

- [1. Fonctionnalités](#1-fonctionnalités)  
- [2. Architecture du projet](#2-architecture-du-projet)  
  - [2.1 Structure des dossiers](#21-structure-des-dossiers)  
  - [2.2 Connexions aux bases](#22-connexions-aux-bases)  
  - [2.3 Pattern DAO](#23-pattern-dao)  
- [3. Installation](#3-installation)  
- [4. Usage de l’API](#4-usage-de-lapi)  
  - [4.1 Customers (MongoDB)](#41-customers-mongodb)  
  - [4.2 Vehicles (MongoDB)](#42-vehicles-mongodb)  
  - [4.3 Contracts (MySQL)](#43-contracts-mysql)  
  - [4.4 Payments (MySQL)](#44-payments-mysql)  
  - [4.5 Analytics (MySQL)](#45-analytics-mysql)  
- [5. Tests](#5-tests)  
- [6. Extensibilité & Sécurité](#6-extensibilité--sécurité) 

---

## 1. Fonctionnalités

- **CRUD** complet pour :  
  - **Customer** (MongoDB)  
  - **Vehicle** (MongoDB) + comptage par kilométrage  
  - **Contract** (MySQL)  
  - **Billing** (MySQL)  
- **Endpoints d’analytics** pour :  
  - Contrats par client ou véhicule  
  - Locations actives, en retard, impayées  
  - Statistiques de retard (moyennes, comptes)  
- **Configuration** via `docker-compose` pour montée en environnement local (MongoDB + MySQL).  
- **Validation** des payloads JSON grâce à **Pydantic**.  
- **Documentation interactive** générée par **Swagger** (`/docs`).

---

## 2. Architecture du projet

### 2.1 Structure des dossiers

easy-loc/ 
├─ db/ 
│ 
├─ mongo/ 
│ 
│ 
├─ connector.py # MongoConnector 
│ 
│ 
├─ customer_dao.py # CustomerDAO 
│ 
│ 
└─ vehicle_dao.py # VehicleDAO 
│ 
└─ mysql/ 
│ 
├─ connector.py # MySQLConnector 
│ 
├─ models.py # SQLAlchemy Base + ORM models 
│ 
├─ contract_dao.py # ContractDAO 
│ 
├─ billing_dao.py # BillingDAO 
│ 
└─ analytics_dao.py # AnalyticsDAO 
├─ docker/ 
│ 
└─ docker-compose.yml # MongoDB + MySQL init 
├─ main.py # FastAPI app 
├─ tests/ # pytest tests 
└─ README.md

### 2.2 Connexions aux bases

- **MongoConnector** (`pymongo`)  
  - Authentification optionnelle  
  - `test_connection()`, `get_collection(name)`  
- **MySQLConnector** (`SQLAlchemy + pymysql`)  
  - `connect()`, `get_session()`  
  - Génère la `SessionLocal` pour les DAOs

### 2.3 Pattern DAO

Chaque DAO encapsule les opérations *CRUD* et requêtes métiers :

- **CustomerDAO** / **VehicleDAO** → MongoDB  
- **ContractDAO**, **BillingDAO**, **AnalyticsDAO** → MySQL

---

## 3. Installation

1. **Cloner le repo**  

   git clone https://github.com/Lykkss/easy-loc.git
   cd easy-loc

2. **Préparer l’environnement**

conda create -n easyloc_env python=3.11 -y
conda activate easyloc_env
pip install -r requirements.txt

3. **Monter les bases**

cd docker
docker-compose up --build -d

4. **Lancer l’API**

uvicorn main:app --reload --host 0.0.0.0 --port 8000

## 4. Usage de l’API

4.1 **Customers (MongoDB)**
Créer
POST /api/customers

{
  "uid": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "Alice",
  "second_name": "Martin",
  "address": "1 rue des Tests, 69000 Lyon",
  "permit_number": "PERM-ABCD-1234"
}

Lire
GET /api/customers/{uid}

4.2 Vehicles (MongoDB)
Créer
POST /api/vehicles

Lire
GET /api/vehicles/{uid}

Mettre à jour
PUT /api/vehicles/{uid}
Payload JSON partiel

Supprimer
DELETE /api/vehicles/{uid}

Compter par km
GET /api/vehicles/count?km=15000&op=gt

4.3 Contracts (MySQL)
Créer
POST /api/contracts

Lire
GET /api/contracts/{id}

Mettre à jour
PUT /api/contracts/{id}

Supprimer
DELETE /api/contracts/{id}

4.4 Payments (MySQL)
Créer
POST /api/payments

Lire
GET /api/payments/{id}

Mettre à jour
PUT /api/payments/{id}

Supprimer
DELETE /api/payments/{id}

4.5 Analytics (MySQL)
Contrats par client :
GET /api/analytics/contracts/customer/{uid}

Locations actives :
GET /api/analytics/contracts/active/{uid}

Locations en retard :
GET /api/analytics/contracts/late

Paiements d’un contrat :
GET /api/analytics/payments/{contract_id}

Contrat entièrement payé :
GET /api/analytics/paid/{contract_id}

Locations impayées :
GET /api/analytics/unpaid

Nombre de retards :
GET /api/analytics/count-delays?start=YYYY-MM-DD&end=YYYY-MM-DD

Retard moyen par client :
GET /api/analytics/avg-delay/customer

Contrats par véhicule :
GET /api/analytics/contracts/vehicle/{uid}

Retard moyen par véhicule :
GET /api/analytics/avg-delay/vehicle

Groupement de contrats :
GET /api/analytics/group-contracts?by=vehicle_uid

## 5. Tests
Lancer tous les tests unitaires :

pytest tests/ --maxfail=1 --disable-warnings -v

MongoDB : tests/mongo/…

MySQL : tests/mysql/…

## 6. Extensibilité & Sécurité

Nouveau SGBD : ajouter un nouveau Connector + DAO, sans impacter les autres.

Validation : payloads Pydantic pour éviter injections.

Logs & erreurs : centralisés via FastAPI/uvicorn.error.
