import pytest
from db.mysql.connector import MySQLConnector
from db.mysql.models import Base
from db.mysql.contract_dao import ContractDAO
from db.mysql.billing_dao import BillingDAO
from datetime import datetime, timedelta

@pytest.fixture(scope="module")
def session():
    connector = MySQLConnector(user="user", password="password", host="localhost", port=3306, database="easyloc")
    connector.connect()
    Base.metadata.create_all(bind=connector.engine)
    session = connector.get_session()
    yield session
    session.close()

@pytest.fixture
def contract_id(session):
    contract_dao = ContractDAO(session)
    contract = contract_dao.create_contract({
        "vehicle_uid": "veh-test",
        "customer_uid": "cus-test",
        "sign_datetime": datetime.now(),
        "loc_begin_datetime": datetime.now(),
        "loc_end_datetime": datetime.now() + timedelta(days=1),
        "returning_datetime": datetime.now() + timedelta(days=1),
        "price": 100.0
    })
    return contract.id

def test_create_and_get_payment(session, contract_id):
    dao = BillingDAO(session)
    payment = dao.create_payment(contract_id, 50.0)
    fetched = dao.get_payment_by_id(payment.id)
    assert fetched is not None
    assert fetched.amount == 50.0
    assert fetched.contract_id == contract_id

def test_update_payment(session, contract_id):
    dao = BillingDAO(session)
    payment = dao.create_payment(contract_id, 30.0)
    updated = dao.update_payment(payment.id, 45.0)
    assert updated
    refreshed = dao.get_payment_by_id(payment.id)
    assert refreshed.amount == 45.0

def test_delete_payment(session, contract_id):
    dao = BillingDAO(session)
    payment = dao.create_payment(contract_id, 25.0)
    deleted = dao.delete_payment(payment.id)
    assert deleted
    assert dao.get_payment_by_id(payment.id) is None
