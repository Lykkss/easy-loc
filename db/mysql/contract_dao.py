from db.mysql.models import Contract
from sqlalchemy.orm import Session
from datetime import datetime

class ContractDAO:
    def __init__(self, session: Session):
        self.session = session

    def create_contract(self, contract_data: dict) -> Contract:
        contract = Contract(**contract_data)
        self.session.add(contract)
        self.session.commit()
        return contract

    def get_contract_by_id(self, contract_id: int) -> Contract | None:
        return self.session.query(Contract).filter_by(id=contract_id).first()

    def update_contract(self, contract_id: int, update_data: dict) -> bool:
        contract = self.get_contract_by_id(contract_id)
        if contract:
            for key, value in update_data.items():
                setattr(contract, key, value)
            self.session.commit()
            return True
        return False

    def delete_contract(self, contract_id: int) -> bool:
        contract = self.get_contract_by_id(contract_id)
        if contract:
            self.session.delete(contract)
            self.session.commit()
            return True
        return False
