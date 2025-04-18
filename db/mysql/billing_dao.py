from db.mysql.models import Billing
from sqlalchemy.orm import Session

class BillingDAO:
    def __init__(self, session: Session):
        self.session = session

    def create_payment(self, contract_id: int, amount: float) -> Billing:
        billing = Billing(contract_id=contract_id, amount=amount)
        self.session.add(billing)
        self.session.commit()
        return billing

    def get_payment_by_id(self, billing_id: int) -> Billing | None:
        return self.session.query(Billing).filter_by(id=billing_id).first()

    def update_payment(self, billing_id: int, new_amount: float) -> bool:
        billing = self.get_payment_by_id(billing_id)
        if billing:
            billing.amount = new_amount
            self.session.commit()
            return True
        return False

    def delete_payment(self, billing_id: int) -> bool:
        billing = self.get_payment_by_id(billing_id)
        if billing:
            self.session.delete(billing)
            self.session.commit()
            return True
        return False
