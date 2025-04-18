from db.mongo.connector import MongoConnector
from bson import ObjectId

class VehicleDAO:
    def __init__(self, connector: MongoConnector):
        self.collection = connector.get_collection("vehicles")

    def create_vehicle(self, vehicle: dict) -> str:
        result = self.collection.insert_one(vehicle)
        return str(result.inserted_id)

    def get_vehicle_by_uid(self, uid: str) -> dict | None:
        return self.collection.find_one({"uid": uid})

    def find_by_plate(self, licence_plate: str) -> dict | None:
        return self.collection.find_one({"licence_plate": licence_plate})

    def update_vehicle(self, uid: str, updates: dict) -> bool:
        result = self.collection.update_one({"uid": uid}, {"$set": updates})
        return result.modified_count > 0

    def delete_vehicle(self, uid: str) -> bool:
        result = self.collection.delete_one({"uid": uid})
        return result.deleted_count > 0

    def count_vehicles_by_km(self, km: int, greater_than=True) -> int:
        query = {"km": {"$gt" if greater_than else "$lt": km}}
        return self.collection.count_documents(query)
