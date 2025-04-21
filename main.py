# main.py
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db.mongo.connector import MongoConnector
from db.mongo.customer_dao import CustomerDAO

logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="EasyLoc API", docs_url="/docs", redoc_url="/redoc")

class CustomerIn(BaseModel):
    uid: str
    first_name: str
    second_name: str
    address: str
    permit_number: str

# Connexion MongoDB AVEC authentification
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
        return {
            "message": "Customer created successfully",
            "customer_id": inserted_id
        }
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
