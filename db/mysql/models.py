from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey

Base = declarative_base()

class Contract(Base):
    __tablename__ = "Contract"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_uid = Column(String(255), nullable=False)
    customer_uid = Column(String(255), nullable=False)
    sign_datetime = Column(DateTime, nullable=False)
    loc_begin_datetime = Column(DateTime, nullable=False)
    loc_end_datetime = Column(DateTime, nullable=False)
    returning_datetime = Column(DateTime)
    price = Column(Float, nullable=False)

class Billing(Base):
    __tablename__ = "Billing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey("Contract.id"), nullable=False)
    amount = Column(Float, nullable=False)

