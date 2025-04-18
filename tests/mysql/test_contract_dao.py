import pytest
from db.mysql.connector import MySQLConnector
from db.mysql.contract_dao import ContractDAO
from db.mysql.models import Base
from datetime import datetime, timedelta

@pytest.fixture(scope="module")
def session():
    connector = MySQLConnector(user="user", password="password", host="localhost", port=3306, database="easyloc")
    connector.connect()
    Base.metadata.create_all(bind=connector.engine)
    session = connector.get_session()
    yield session
    session.close()

def test_create_and_get_contract(session):
    dao = ContractDAO(session)

    data = {
        "vehicle_uid": "veh123",
        "customer_uid": "cus123",
        "sign_datetime": datetime.now(),
        "loc_begin_datetime": datetime.now(),
        "loc_end_datetime": datetime.now() + timedelta(days=1),
        "returning_datetime": datetime.now() + timedelta(days=1, hours=2),
        "price": 120.50
    }

    contract = dao.create_contract(data)
    retrieved = dao.get_contract_by_id(contract.id)

    assert retrieved is not None
    assert retrieved.customer_uid == "cus123"

def test_update_contract(session):
    dao = ContractDAO(session)
    contract = dao.get_contract_by_id(1)
    updated = dao.update_contract(contract.id, {"price": 200})
    assert updated
    updated_contract = dao.get_contract_by_id(contract.id)
    assert updated_contract.price == 200

def test_delete_contract(session):
    dao = ContractDAO(session)
    contract = dao.create_contract({
        "vehicle_uid": "veh999",
        "customer_uid": "cus999",
        "sign_datetime": datetime.now(),
        "loc_begin_datetime": datetime.now(),
        "loc_end_datetime": datetime.now() + timedelta(days=2),
        "returning_datetime": datetime.now() + timedelta(days=2),
        "price": 90.0
    })

    deleted = dao.delete_contract(contract.id)
    assert deleted
    assert dao.get_contract_by_id(contract.id) is None
