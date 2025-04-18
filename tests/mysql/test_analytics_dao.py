import pytest
from db.mysql.connector import MySQLConnector
from db.mysql.models import Base
from db.mysql.contract_dao import ContractDAO
from db.mysql.billing_dao import BillingDAO
from db.mysql.analytics_dao import AnalyticsDAO
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
def setup_data(session):
    contract_dao = ContractDAO(session)
    billing_dao = BillingDAO(session)

    # Contrat payé entièrement
    c1 = contract_dao.create_contract({
        "vehicle_uid": "veh123",
        "customer_uid": "cus123",
        "sign_datetime": datetime.now(),
        "loc_begin_datetime": datetime.now(),
        "loc_end_datetime": datetime.now() + timedelta(days=1),
        "returning_datetime": datetime.now() + timedelta(days=1),
        "price": 100.0
    })
    billing_dao.create_payment(c1.id, 100.0)

    # Contrat NON payé
    c2 = contract_dao.create_contract({
        "vehicle_uid": "veh123",
        "customer_uid": "cus456",
        "sign_datetime": datetime.now(),
        "loc_begin_datetime": datetime.now(),
        "loc_end_datetime": datetime.now() + timedelta(days=1),
        "returning_datetime": datetime.now() + timedelta(days=1),
        "price": 100.0
    })

    # Contrat EN RETARD (+2h)
    c3 = contract_dao.create_contract({
        "vehicle_uid": "veh789",
        "customer_uid": "cus456",
        "sign_datetime": datetime.now(),
        "loc_begin_datetime": datetime.now(),
        "loc_end_datetime": datetime.now() + timedelta(hours=1),
        "returning_datetime": datetime.now() + timedelta(hours=3),
        "price": 80.0
    })

    return {
        "paid": c1.id,
        "unpaid": c2.id,
        "late": c3.id
    }

def test_is_fully_paid(session, setup_data):
    dao = AnalyticsDAO(session)
    assert dao.is_fully_paid(setup_data["paid"]) == True
    assert dao.is_fully_paid(setup_data["unpaid"]) == False

def test_get_unpaid_contracts(session):
    dao = AnalyticsDAO(session)
    unpaid_contracts = dao.get_unpaid_contracts()
    assert any(c.customer_uid == "cus456" for c in unpaid_contracts)

def test_get_late_contracts(session):
    dao = AnalyticsDAO(session)
    late_contracts = dao.get_late_contracts()
    assert any(c.vehicle_uid == "veh789" for c in late_contracts)

def test_count_delays(session):
    dao = AnalyticsDAO(session)
    start = datetime.now() - timedelta(days=1)
    end = datetime.now() + timedelta(days=2)
    count = dao.count_delays(start, end)
    assert count >= 1

def test_avg_delay_by_vehicle(session):
    dao = AnalyticsDAO(session)
    results = dao.avg_delay_by_vehicle()
    assert any(row.avg_delay > 60 for row in results)
