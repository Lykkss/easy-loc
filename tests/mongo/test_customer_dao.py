import pytest
from db.mongo.connector import MongoConnector
from db.mongo.customer_dao import CustomerDAO
import uuid

@pytest.fixture(scope="module")
def dao():
    # Remplacer 'user' par 'username' ici
    connector = MongoConnector(username="user", password="password", database="easyloc")
    return CustomerDAO(connector)

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

def test_update_customer(dao):
    customer = dao.find_by_name("Alice", "Martin")[0]
    updated = dao.update_customer(customer["uid"], {"address": "2 avenue modifiée"})
    assert updated is True
    modified = dao.get_customer_by_uid(customer["uid"])
    assert modified["address"] == "2 avenue modifiée"

def test_delete_customer(dao):
    customer = dao.find_by_name("Alice", "Martin")[0]
    deleted = dao.delete_customer(customer["uid"])
    assert deleted is True
    assert dao.get_customer_by_uid(customer["uid"]) is None
