from db.mongo.connector import MongoConnector
from bson import ObjectId

class CustomerDAO:
    def __init__(self, connector: MongoConnector):
        self.collection = connector.get_collection("customers")

    def create_customer(self, customer: dict) -> str:
        result = self.collection.insert_one(customer)
        return str(result.inserted_id)

    def get_customer_by_uid(self, uid: str) -> dict | None:
        return self.collection.find_one({"uid": uid})

    def find_by_name(self, first_name: str, second_name: str) -> list[dict]:
        return list(self.collection.find({
            "first_name": first_name,
            "second_name": second_name
        }))

    def update_customer(self, uid: str, updates: dict) -> bool:
        result = self.collection.update_one({"uid": uid}, {"$set": updates})
        return result.modified_count > 0

    def delete_customer(self, uid: str) -> bool:
        result = self.collection.delete_one({"uid": uid})
        return result.deleted_count > 0
