from sqlalchemy.orm import Session
from sqlalchemy import func, text
from db.mysql.models import Contract, Billing
from datetime import datetime, timedelta

class AnalyticsDAO:
    def __init__(self, session: Session):
        self.session = session

    def get_contracts_by_customer(self, customer_uid: str):
        """Lister tous les contrats d’un client donné"""
        return self.session.query(Contract).filter_by(customer_uid=customer_uid).all()

    def get_active_contracts_by_customer(self, customer_uid: str):
        """Lister les locations en cours d’un client"""
        now = datetime.now()
        return self.session.query(Contract).filter(
            Contract.customer_uid == customer_uid,
            Contract.loc_begin_datetime <= now,
            Contract.returning_datetime == None
        ).all()

    def get_late_contracts(self):
        """Lister toutes les locations en retard (> 1h)"""
        return self.session.query(Contract).filter(
            Contract.returning_datetime != None,
            Contract.returning_datetime > Contract.loc_end_datetime + timedelta(hours=1)
        ).all()

    def get_billing_for_contract(self, contract_id: int):
        """Lister tous les paiements pour un contrat"""
        return self.session.query(Billing).filter_by(contract_id=contract_id).all()

    def is_fully_paid(self, contract_id: int) -> bool:
        """Vérifier si un contrat est entièrement payé"""
        contract = self.session.query(Contract).filter_by(id=contract_id).first()
        if not contract:
            return False
        total_paid = self.session.query(func.sum(Billing.amount)).filter_by(contract_id=contract_id).scalar() or 0
        return total_paid >= contract.price

    def get_unpaid_contracts(self):
        """Lister les contrats impayés (total < prix)"""
        contracts = self.session.query(Contract).all()
        unpaid = []
        for contract in contracts:
            total_paid = self.session.query(func.sum(Billing.amount)).filter_by(contract_id=contract.id).scalar() or 0
            if total_paid < contract.price:
                unpaid.append(contract)
        return unpaid

    def count_delays(self, start: datetime, end: datetime):
        """Compter les retards entre deux dates"""
        return self.session.query(Contract).filter(
            Contract.returning_datetime > Contract.loc_end_datetime + timedelta(hours=1),
            Contract.loc_end_datetime.between(start, end)
        ).count()

    def avg_delays_by_customer(self):
        """Moyenne de retard (minutes) par client"""
        return self.session.query(
            Contract.customer_uid,
            func.avg(
                func.timestampdiff(
                    text("MINUTE"),
                    Contract.loc_end_datetime,
                    Contract.returning_datetime
                )
            ).label("avg_delay")
        ).filter(
            Contract.returning_datetime > Contract.loc_end_datetime + timedelta(hours=1)
        ).group_by(Contract.customer_uid).all()

    def contracts_by_vehicle(self, vehicle_uid: str):
        """Lister tous les contrats d’un véhicule"""
        return self.session.query(Contract).filter_by(vehicle_uid=vehicle_uid).all()

    def avg_delay_by_vehicle(self):
        """Moyenne des retards (minutes) par véhicule"""
        return self.session.query(
            Contract.vehicle_uid,
            func.avg(
                func.timestampdiff(
                    text("MINUTE"),
                    Contract.loc_end_datetime,
                    Contract.returning_datetime
                )
            ).label("avg_delay")
        ).filter(
            Contract.returning_datetime > Contract.loc_end_datetime + timedelta(hours=1)
        ).group_by(Contract.vehicle_uid).all()

    def group_contracts_by(self, field: str = "vehicle_uid"):
        """Récupérer tous les contrats regroupés par champ"""
        if field not in ["vehicle_uid", "customer_uid"]:
            raise ValueError("Champ non autorisé pour le groupement.")
        return self.session.query(
            getattr(Contract, field),
            func.count().label("total_contracts")
        ).group_by(getattr(Contract, field)).all()
