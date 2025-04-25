# main.py
import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from db.mongo.connector import MongoConnector
from db.mongo.customer_dao import CustomerDAO
from db.mongo.vehicle_dao import VehicleDAO

from db.mysql.connector import MySQLConnector
from db.mysql.contract_dao import ContractDAO
from db.mysql.billing_dao import BillingDAO
from db.mysql.analytics_dao import AnalyticsDAO
from db.mysql.models import Base

logger = logging.getLogger("uvicorn.error")

app = FastAPI(
    title="EasyLoc API",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ---------- Pydantic Schemas ----------

class CustomerIn(BaseModel):
    uid: str
    first_name: str
    second_name: str
    address: str
    permit_number: str


class VehicleIn(BaseModel):
    uid: str
    licence_plate: str
    informations: str
    km: int


class VehicleUpdate(BaseModel):
    licence_plate: Optional[str]
    informations: Optional[str]
    km: Optional[int]


class VehicleCountOut(BaseModel):
    km: int
    op: str
    count: int


class ContractIn(BaseModel):
    vehicle_uid: str
    customer_uid: str
    sign_datetime: datetime
    loc_begin_datetime: datetime
    loc_end_datetime: datetime
    returning_datetime: datetime
    price: float


class ContractUpdate(BaseModel):
    vehicle_uid: Optional[str]
    customer_uid: Optional[str]
    sign_datetime: Optional[datetime]
    loc_begin_datetime: Optional[datetime]
    loc_end_datetime: Optional[datetime]
    returning_datetime: Optional[datetime]
    price: Optional[float]


class PaymentIn(BaseModel):
    contract_id: int
    amount: float


class PaymentUpdate(BaseModel):
    amount: float


# ---------- MongoDB Setup ----------

mongo = MongoConnector(
    host="localhost",
    port=27017,
    database="easyloc",
    username="user",
    password="password",
)
if not mongo.test_connection():
    logger.error("Impossible de se connecter à MongoDB")
    raise RuntimeError("MongoDB unreachable")

customer_dao = CustomerDAO(mongo)
vehicle_dao = VehicleDAO(mongo)


# ---------- MySQL Setup ----------

mysql = MySQLConnector(
    user="user",
    password="password",
    host="localhost",
    port=3306,
    database="easyloc",
)
mysql.connect()
Base.metadata.create_all(bind=mysql.engine)
session = mysql.get_session()

contract_dao = ContractDAO(session)
billing_dao = BillingDAO(session)
analytics_dao = AnalyticsDAO(session)


# --- Customers Endpoints ---

@app.post("/api/customers", status_code=201, tags=["customers"])
def create_customer(c: CustomerIn):
    cid = customer_dao.create_customer(c.dict())
    return {"message": "Customer created successfully", "customer_id": cid}


@app.get("/api/customers/{uid}", response_model=CustomerIn, tags=["customers"])
def read_customer(uid: str):
    cust = customer_dao.get_customer_by_uid(uid)
    if not cust:
        raise HTTPException(404, detail="Customer not found")
    return CustomerIn(**cust)


# --- Vehicles Endpoints ---

@app.post("/api/vehicles", status_code=201, tags=["vehicles"])
def create_vehicle(v: VehicleIn):
    vid = vehicle_dao.create_vehicle(v.dict())
    return {"message": "Vehicle created successfully", "vehicle_id": vid}


@app.get("/api/vehicles/{uid}", response_model=VehicleIn, tags=["vehicles"])
def read_vehicle(uid: str):
    v = vehicle_dao.get_vehicle_by_uid(uid)
    if not v:
        raise HTTPException(404, detail="Vehicle not found")
    return VehicleIn(**v)


@app.put("/api/vehicles/{uid}", response_model=Dict[str, str], tags=["vehicles"])
def update_vehicle(uid: str, upd: VehicleUpdate):
    if not vehicle_dao.update_vehicle(uid, upd.dict(exclude_unset=True)):
        raise HTTPException(404, detail="Vehicle not found or no change")
    return {"message": "Vehicle updated successfully"}


@app.delete("/api/vehicles/{uid}", response_model=Dict[str, str], tags=["vehicles"])
def delete_vehicle(uid: str):
    if not vehicle_dao.delete_vehicle(uid):
        raise HTTPException(404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}


@app.get(
    "/api/vehicles/count",
    response_model=VehicleCountOut,
    tags=["vehicles"],
)
def count_vehicles_by_km(
    km: int = Query(..., description="kilométrage seuil"),
    op: str = Query(
        "gt",
        regex="^(gt|lt)$",
        description="‘gt’ pour >, ‘lt’ pour <"
    )
):
    count = vehicle_dao.count_vehicles_by_km(km, greater_than=(op == "gt"))
    return VehicleCountOut(km=km, op=op, count=count)


# --- Contracts (MySQL) Endpoints ---

@app.post("/api/contracts", status_code=201, tags=["contracts"])
def create_contract(c: ContractIn):
    co = contract_dao.create_contract(c.dict())
    return {"contract_id": co.id}


@app.get("/api/contracts/{cid}", tags=["contracts"])
def get_contract(cid: int):
    co = contract_dao.get_contract_by_id(cid)
    if not co:
        raise HTTPException(404, detail="Contract not found")
    return co


@app.put("/api/contracts/{cid}", response_model=Dict[str, str], tags=["contracts"])
def update_contract(cid: int, upd: ContractUpdate):
    if not contract_dao.update_contract(cid, upd.dict(exclude_unset=True)):
        raise HTTPException(404, detail="Contract not found or no change")
    return {"message": "Contract updated successfully"}


@app.delete("/api/contracts/{cid}", response_model=Dict[str, str], tags=["contracts"])
def delete_contract(cid: int):
    if not contract_dao.delete_contract(cid):
        raise HTTPException(404, detail="Contract not found")
    return {"message": "Contract deleted successfully"}


# --- Payments (MySQL) Endpoints ---

@app.post("/api/payments", status_code=201, tags=["payments"])
def create_payment(p: PaymentIn):
    pay = billing_dao.create_payment(p.contract_id, p.amount)
    return {"payment_id": pay.id}


@app.get("/api/payments/{pid}", tags=["payments"])
def get_payment(pid: int):
    pay = billing_dao.get_payment_by_id(pid)
    if not pay:
        raise HTTPException(404, detail="Payment not found")
    return pay


@app.put("/api/payments/{pid}", response_model=Dict[str, str], tags=["payments"])
def update_payment(pid: int, upd: PaymentUpdate):
    if not billing_dao.update_payment(pid, upd.amount):
        raise HTTPException(404, detail="Payment not found or no change")
    return {"message": "Payment updated successfully"}


@app.delete("/api/payments/{pid}", response_model=Dict[str, str], tags=["payments"])
def delete_payment(pid: int):
    if not billing_dao.delete_payment(pid):
        raise HTTPException(404, detail="Payment not found")
    return {"message": "Payment deleted successfully"}


# --- Analytics (MySQL) Endpoints ---

@app.get("/api/analytics/contracts/customer/{uid}", tags=["analytics"])
def contracts_by_customer(uid: str):
    return analytics_dao.get_contracts_by_customer(uid)


@app.get("/api/analytics/contracts/active/{uid}", tags=["analytics"])
def active_contracts(uid: str):
    return analytics_dao.get_active_contracts_by_customer(uid)


@app.get("/api/analytics/contracts/late", tags=["analytics"])
def late_contracts():
    return analytics_dao.get_late_contracts()


@app.get("/api/analytics/payments/{cid}", tags=["analytics"])
def payments_for_contract(cid: int):
    return analytics_dao.get_billing_for_contract(cid)


@app.get("/api/analytics/paid/{cid}", tags=["analytics"])
def is_paid(cid: int):
    return {"fully_paid": analytics_dao.is_fully_paid(cid)}


@app.get("/api/analytics/unpaid", tags=["analytics"])
def unpaid_contracts():
    return analytics_dao.get_unpaid_contracts()


@app.get("/api/analytics/count-delays", tags=["analytics"])
def count_delays(
    start: date = Query(..., description="Date de début"),
    end: date = Query(..., description="Date de fin")
):
    return {"count": analytics_dao.count_delays(start, end)}


@app.get("/api/analytics/avg-delay/customer", tags=["analytics"])
def avg_delay_customer():
    return analytics_dao.avg_delays_by_customer()


@app.get("/api/analytics/contracts/vehicle/{vid}", tags=["analytics"])
def contracts_by_vehicle(vid: str):
    return analytics_dao.contracts_by_vehicle(vid)


@app.get("/api/analytics/avg-delay/vehicle", tags=["analytics"])
def avg_delay_vehicle():
    return analytics_dao.avg_delay_by_vehicle()


@app.get("/api/analytics/group-contracts", tags=["analytics"])
def group_contracts(
    by: str = Query(
        "vehicle_uid",
        regex="^(vehicle_uid|customer_uid)$",
        description="‘vehicle_uid’ ou ‘customer_uid’"
    )
):
    return analytics_dao.group_contracts_by(by)
