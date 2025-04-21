# main.py
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from db.mongo.connector import MongoConnector
from db.mongo.customer_dao import CustomerDAO
from db.mongo.vehicle_dao import VehicleDAO

logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="EasyLoc API", docs_url="/docs", redoc_url="/redoc")

# --- Pydantic schemas ---
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

# --- MongoDB connection ---
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

# --- DAOs ---
customer_dao = CustomerDAO(mongo)
vehicle_dao = VehicleDAO(mongo)

# --- Customer endpoints ---
@app.post(
    "/api/customers",
    status_code=201,
    tags=["customers"],
    response_model=dict,
)
def create_customer(customer: CustomerIn):
    """
    Crée un customer et renvoie son ID Mongo généré.
    """
    try:
        inserted_id = customer_dao.create_customer(customer.dict())
        return {"message": "Customer created successfully", "customer_id": inserted_id}
    except Exception:
        logger.exception("Erreur lors de la création du customer")
        raise HTTPException(500, detail="Internal server error")

@app.get(
    "/api/customers/{customer_uid}",
    response_model=CustomerIn,
    tags=["customers"],
)
def get_customer_by_uid(customer_uid: str):
    try:
        cust = customer_dao.get_customer_by_uid(customer_uid)
        if not cust:
            raise HTTPException(404, detail="Customer not found")
        return CustomerIn(**cust)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur inattendue dans get_customer_by_uid")
        raise HTTPException(500, detail="Internal server error")

# --- Vehicle endpoints ---
@app.post(
    "/api/vehicles",
    status_code=201,
    tags=["vehicles"],
    response_model=dict,
)
def create_vehicle(vehicle: VehicleIn):
    """
    Crée un vehicle et renvoie son ID Mongo généré.
    """
    try:
        vid = vehicle_dao.create_vehicle(vehicle.dict())
        return {"message": "Vehicle created successfully", "vehicle_id": vid}
    except Exception:
        logger.exception("Erreur lors de la création du vehicle")
        raise HTTPException(500, detail="Internal server error")

@app.get(
    "/api/vehicles/{vehicle_uid}",
    response_model=VehicleIn,
    tags=["vehicles"],
)
def get_vehicle_by_uid(vehicle_uid: str):
    try:
        v = vehicle_dao.get_vehicle_by_uid(vehicle_uid)
        if not v:
            raise HTTPException(404, detail="Vehicle not found")
        return VehicleIn(**v)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur inattendue dans get_vehicle_by_uid")
        raise HTTPException(500, detail="Internal server error")

@app.put(
    "/api/vehicles/{vehicle_uid}",
    status_code=200,
    tags=["vehicles"],
    response_model=dict,
)
def update_vehicle(vehicle_uid: str, updates: dict):
    try:
        ok = vehicle_dao.update_vehicle(vehicle_uid, updates)
        if not ok:
            raise HTTPException(404, detail="Vehicle not found or no change")
        return {"message": "Vehicle updated successfully"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur inattendue dans update_vehicle")
        raise HTTPException(500, detail="Internal server error")

@app.delete(
    "/api/vehicles/{vehicle_uid}",
    status_code=200,
    tags=["vehicles"],
    response_model=dict,
)
def delete_vehicle(vehicle_uid: str):
    try:
        ok = vehicle_dao.delete_vehicle(vehicle_uid)
        if not ok:
            raise HTTPException(404, detail="Vehicle not found")
        return {"message": "Vehicle deleted successfully"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Erreur inattendue dans delete_vehicle")
        raise HTTPException(500, detail="Internal server error")

@app.get(
    "/api/vehicles/count",
    status_code=200,
    tags=["vehicles"],
    response_model=dict,
)
def count_vehicles_by_km(km: int, op: Optional[str] = "gt"):
    """
    Compte les véhicules dont km > ou < valeur selon `op` ("gt" ou "lt").
    """
    if op not in ("gt", "lt"):
        raise HTTPException(400, detail="Paramètre op invalide, doit être 'gt' ou 'lt'")
    count = vehicle_dao.count_vehicles_by_km(km, greater_than=(op == "gt"))
    return {"km": km, "op": op, "count": count}
