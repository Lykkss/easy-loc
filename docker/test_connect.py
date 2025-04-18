# test_connect.py

from db.mysql.connector import MySQLConnector
from db.mongodb.connector import MongoDBConnector

# 🔐 Connexion MySQL
mysql = MySQLConnector(user="user", password="password", host="localhost", port=3307, database="easyloc")
mysql.connect()

# 🔐 Connexion MongoDB
mongo = MongoDBConnector(host="localhost", port=27018)
mongo.test_connection()
