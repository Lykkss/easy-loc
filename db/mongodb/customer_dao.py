from pymongo.collection import Collection
from db.mongodb.schemas import CustomerSchema

class CustomerDAO:
    def __init__(self, collection: Collection):
        self.collection = collection

    def create_customer(self, customer: CustomerSchema):
        self.collection.insert_one(customer.model_dump())

    def update_customer(self, uid: str, updates: dict):
        self.collection.update_one({"uid": uid}, {"$set": updates})

    def delete_customer(self, uid: str):
        self.collection.delete_one({"uid": uid})

    def find_by_name(self, first_name: str, second_name: str):
        return self.collection.find_one({"first_name": first_name, "second_name": second_name})
