import pytest
from db.mongo.connector import MongoConnector
from db.mongo.vehicle_dao import VehicleDAO
import uuid

@pytest.fixture(scope="module")
def dao():
    connector = MongoConnector(username="user", password="password", database="easyloc")
    return VehicleDAO(connector)

def test_create_and_get_vehicle(dao):
    uid = str(uuid.uuid4())
    vehicle = {
        "uid": uid,
        "licence_plate": "TEST-1234",
        "informations": "Voiture test",
        "km": 15000
    }
    dao.create_vehicle(vehicle)
    found = dao.get_vehicle_by_uid(uid)
    assert found is not None
    assert found["licence_plate"] == "TEST-1234"

def test_find_by_plate(dao):
    result = dao.find_by_plate("TEST-1234")
    assert result is not None
    assert result["licence_plate"] == "TEST-1234"

def test_update_vehicle(dao):
    vehicle = dao.find_by_plate("TEST-1234")
    updated = dao.update_vehicle(vehicle["uid"], {"km": 30000})
    assert updated is True
    updated_doc = dao.get_vehicle_by_uid(vehicle["uid"])
    assert updated_doc["km"] == 30000

def test_count_by_km(dao):
    count = dao.count_vehicles_by_km(10000, greater_than=True)
    assert count >= 1  # Le véhicule de test a 30000 km

def test_delete_vehicle(dao):
    vehicle = dao.find_by_plate("TEST-1234")
    deleted = dao.delete_vehicle(vehicle["uid"])
    assert deleted is True
